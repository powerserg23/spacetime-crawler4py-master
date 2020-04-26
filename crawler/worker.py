from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper,getOutput
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.prev_url = ""
        self.counter = 0
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                getOutput()
                break
            if self.prev_url == "":
                self.prev_url = tbd_url
            else:
                if self.prev_url.split('/')[2] == tbd_url.split('/')[2]:
                    time.sleep(0.5)
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            self.counter += 1
            print(str(self.counter))
            scraped_urls = scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
