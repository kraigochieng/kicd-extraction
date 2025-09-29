from pathlib import Path

import scrapy


class CurriculumSpider(scrapy.Spider):
    name = "curriculum"

    start_urls = ["https://arena.co.ke/curriculum-designs/"]

    def parse(self, response):
        for curriculum in response.xpath(
            "//a[normalize-space(text())='Download']/parent::*"
        ):
            name = curriculum.xpath(".//strong/text()").get()
            link = curriculum.xpath(".//a/@href").get()

            if name and link:
                yield {
                    "name": name.strip(),
                    "link": response.urljoin(link),
                }

                # Schedule download
                yield scrapy.Request(
                    url=response.urljoin(link),
                    callback=self.save_file,
                    cb_kwargs={"filename": f"{name.strip()}.pdf"},
                )
            print("-" * 50)

    def save_file(self, response, filename):
        path = Path("downloads") / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Saving file {path}")
        path.write_bytes(response.body)
