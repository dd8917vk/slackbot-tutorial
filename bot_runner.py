from classes.RaptorBot import RaptorBot
import time
import schedule

if __name__ == "__main__":
    b = RaptorBot()
    def job():
        print("I'm working...")
    # schedule.every().day.at("21:08").do(b.scrape)
    # schedule.every(5).seconds.do(b.scrape)

    while True:
        time.sleep(1)
        b.scrape()
        # schedule.run_pending()
    # print(b.scrape())