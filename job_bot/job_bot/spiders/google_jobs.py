from pathlib import Path

import scrapy
import csv


class GoogleSpider(scrapy.Spider):
    name = "google_jobs"

    custom_settings = {'ROBOTSTXT_OBEY': False, 'LOG_LEVEL': 'INFO',

                       'CONCURRENT_REQUESTS_PER_DOMAIN': 10,

                       'RETRY_TIMES': 5}

    def start_requests(self):
        urls = [
            'https://www.google.com/search?q=software+developer+site%3Aboards.greenhouse.io+-senior&newwindow=1&sxsrf=APwXEdfgNm-PGHbZRks6bDav6nb4toy4tg%3A1680309285734&source=hp&ei=JXwnZLGtKrXfkPIP1pW6iAM&iflsig=AOEireoAAAAAZCeKNaIogxKNpNHvBbHtgZHOqBy0NZ5u&oq=so&gs_lcp=Cgdnd3Mtd2l6EAEYATIECCMQJzIECCMQJzIRCC4QgwEQxwEQsQMQ0QMQgAQyCAgAEIAEELEDMgsIABCABBCxAxCDATIUCC4QgAQQsQMQgwEQxwEQ0QMQ1AIyCwguEIAEELEDEIMBMgsILhCABBDHARDRAzIOCC4QgAQQsQMQxwEQ0QMyCwguEIAEEMcBEK8BOhEILhCABBCxAxCDARDHARDRA1AAWKAHYMUvaABwAHgAgAGlAYgB8gGSAQMxLjGYAQCgAQE&sclient=gws-wiz',
            'https://www.google.com/search?q=software+developer+site%3Ajobs.lever.co+-senior&newwindow=1&sxsrf=APwXEdc9UJLo_OIV6zjKa4PwmAInsAybiw%3A1680309297952&ei=MXwnZMjFOZXAkPIP6oekqAU&oq=software+&gs_lcp=Cgxnd3Mtd2l6LXNlcnAQARgBMgQIIxAnMgQIIxAnMgoIABCKBRCxAxBDMg0IABCKBRCxAxDJAxBDMggIABCKBRCSAzIICAAQgAQQsQMyCAgAEIAEELEDMggIABCKBRCRAjILCAAQigUQsQMQkQIyBwgAEIoFEEM6CAgAEIAEEJIDOgUIABCABEoECEEYAVC_G1jvHWDfL2gCcAB4AIABmQGIAfMBkgEDMS4xmAEAoAEBwAEB&sclient=gws-wiz-serp',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Follow links to job listing pages
        for link in response.css("a::attr(href)").getall():
            if "/url?q=" in link:
                url = link.split("/url?q=")[-1].split("&sa=")[0]
                yield response.follow(url, self.parse_job_listing)

    def parse_job_listing(self, response):
        # Extract data from job listing page
        job_title = response.css("h1::text").get()
        company = response.css("span.company::text").get()
        posted_date = response.css("span.date::text").get()
        salary = response.css("span.salary::text").get()
        job_description = "\n".join(
            response.css("div.job-description *::text").getall()
        )
        job_link = response.url

        # Yield the extracted data as a dictionary
        yield {
            "job_title": job_title,
            "company": company,
            "posted_date": posted_date,
            "salary": salary,
            "job_description": job_description,
            "job_link": job_link
        }

        # Write job information to CSV file
        with open("job_listings.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([job_title, company, posted_date, salary, job_description, job_link])