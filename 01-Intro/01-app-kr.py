import asyncio
import time
import requests
from bs4 import BeautifulSoup
import scrapy
from scrapy.crawler import CrawlerProcess
from crawl4ai import AsyncWebCrawler

# 비교 설정
TARGET_URL = "https://news.ycombinator.com/"
LIMIT = 5

print(f"--- 웹 스크래핑 라이브러리 비교 ---\n대상 URL: {TARGET_URL}\n")

# 1. BeautifulSoup + Requests
# 가장 적합한 경우: 간단한 정적 페이지, 초보자, 가벼운 작업
def run_beautifulsoup():
    print("[BeautifulSoup] 시작 중...")
    start = time.time()
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(TARGET_URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    data = []
    # Hacker News 구조: 제목은 <span class="titleline"><a ...> 안에 있음
    for el in soup.select('.titleline > a')[:LIMIT]:
        data.append({'title': el.get_text(), 'href': el.get('href')})
        
    duration = time.time() - start
    print(f"[BeautifulSoup] {duration:.4f}초 완료. {len(data)}개 항목 추출.")
    return data

# 2. Crawl4AI
# 가장 적합한 경우: LLM 데이터 추출, 동적 JS 페이지 (Playwright 기반), 깨끗한 마크다운
async def run_crawl4ai():
    print("[Crawl4AI] 시작 중...")
    start = time.time()
    
    # AsyncWebCrawler가 브라우저 세션을 자동으로 관리
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=TARGET_URL)
        
        # 일관성을 위해 HTML을 BS4로 파싱
        # 참고: Crawl4AI는 JS를 실행하므로 동적 콘텐츠를 BS4보다 더 잘 처리함
        soup = BeautifulSoup(result.html, 'html.parser')
        
        data = []
        for el in soup.select('.titleline > a')[:LIMIT]:
            data.append({'title': el.get_text(), 'href': el.get('href')})
            
    duration = time.time() - start
    print(f"[Crawl4AI] {duration:.4f}초 완료. {len(data)}개 항목 추출.")
    return data

# 3. Scrapy
# 가장 적합한 경우: 대규모, 복잡한 스파이더, 동시성, 파이프라인
# 참고: 단일 스크립트에서 Scrapy를 사용하려면 약간의 보일러플레이트가 필요함
class HNSpider(scrapy.Spider):
    name = "hn_spider"
    start_urls = [TARGET_URL]
    custom_settings = {'LOG_LEVEL': 'ERROR'}  # 로깅 억제
    extracted_data = []

    def parse(self, response):
        # Scrapy는 CSS 선택자나 XPath를 기본적으로 사용
        for el in response.css('.titleline > a')[:LIMIT]:
            item = {
                'title': el.css('::text').get(), 
                'href': el.css('::attr(href)').get()
            }
            self.extracted_data.append(item)

def run_scrapy():
    print("[Scrapy] 시작 중...")
    start = time.time()
    
    # CrawlerProcess가 Twisted 리액터를 제어
    process = CrawlerProcess()
    process.crawl(HNSpider)
    process.start()  # 완료될 때까지 실행 차단
    
    duration = time.time() - start
    print(f"[Scrapy] {duration:.4f}초 완료. {len(HNSpider.extracted_data)}개 항목 추출.")
    return HNSpider.extracted_data

if __name__ == "__main__":
    # 1. BeautifulSoup 실행 (동기)
    bs_results = run_beautifulsoup()
    
    # 2. Crawl4AI 실행 (비동기)
    # asyncio.run을 사용하여 이벤트 루프 관리
    c4_results = asyncio.run(run_crawl4ai())

    # 3. Scrapy 실행 (프로세스 차단)
    # 같은 프로세스에서 재시작할 수 없는 Twisted 리액터를 시작하므로 마지막에 실행해야 함
    sc_results = run_scrapy()

    print("\n--- 구문 비교 요약 ---")
    print("BS4:      requests.get() -> BeautifulSoup(html) -> soup.select()")
    print("Crawl4AI: crawler.arun() -> result.html/.markdown")
    print("Scrapy:   Spider 클래스 -> parse 메서드 -> response.css() / yield")