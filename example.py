import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, date, timedelta
import re
from math import cos, pi, floor
import sys
import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import winsound
import easygui


def write_file(msg, filename):
    f = open(filename, "a")
    f.write(msg)
    f.close()
    print(msg)


def replacement(original_str, replacing_word_list, to_be_replaced):
    # original_str = jackpot_tags[1].text
    # replacing_word_list = ['\r', '\n', '\t', ',', '$', ' ', ':', 'Jackpot']
    # to_be_replaced = ''
    big_regex = re.compile('|'.join(map(re.escape, replacing_word_list)))
    final_str = big_regex.sub(to_be_replaced, original_str)

    return final_str


def parse_challenge(page):
    top = page.split('<script>')[1].split('\n')
    challenge = top[1].split(';')[0].split('=')[1]
    challenge_id = top[2].split(';')[0].split('=')[1]
    return {'challenge': challenge, 'challenge_id': challenge_id, 'challenge_result': get_challenge_answer(challenge)}


def get_challenge_answer(challenge):
    arr = list(challenge)
    last_digit = int(arr[-1])
    arr.sort()
    min_digit = int(arr[0])
    subvar_1 = (2 * int(arr[2])) + int(arr[1])
    subvar_2 = str(2 * int(arr[2])) + arr[1]
    power = ((int(arr[0]) * 1) + 2) ** int(arr[1])
    x = (int(challenge) * 3 + subvar_1)
    y = cos(pi * subvar_1)
    answer = x * y
    answer -= power
    answer += (min_digit - last_digit)
    answer = str(int(floor(answer))) + subvar_2
    return answer


def request(url):
    s = requests.Session()
    r = s.get(url)

    if 'X-AA-Challenge' in r.text:
        challenge = parse_challenge(r.text)
        r = s.get(url, headers={
            'X-AA-Challenge': challenge['challenge'],
            'X-AA-Challenge-ID': challenge['challenge_id'],
            'X-AA-Challenge-Result': challenge['challenge_result']
        })

        yum = r.cookies
        r = s.get(url, cookies=yum)
    return r.content


def get_current_race_day_venue_race_no():
    url = 'https://bet.hkjc.com/racing/index.aspx?lang=en'

    r = request(url)
    soup = BeautifulSoup(r, 'html.parser')

    # race no
    race_nums_tag = soup.find("div", {"class": "racebg"})
    race_nums = race_nums_tag.find_all("div", {"id": re.compile('raceSel')})
    total_race_no = len(race_nums)

    # race_day, venue
    race_info = soup.find("div", {"class": "mtgInfoDV"})
    elements = race_info.find_all('nobr')
    race_day = datetime.strptime(elements[0].text.split(',')[0].strip(), '%d/%m/%Y').date()

    if elements[1].text == 'Sha Tin':
        venue = 'ST'
    elif elements[1].text == 'Happy Valley':
        venue = 'HV'
    else:
        venue = elements[1].text
    print('Todays Info: ', race_day, venue, total_race_no)
    return race_day, venue, total_race_no


def get_pools_start_race_no():
    # get starting race no of Double
    url = "https://bet.hkjc.com/racing/pages/odds_dbl.aspx?lang=en"
    r = request(url)
    soup = BeautifulSoup(r, "html.parser")

    divs = soup.find("div", attrs={"class": 'racebg'}).find_all("div", attrs={"class": re.compile('raceNoO')})
    start_race_double = []
    for div in divs:
        start_race_double.append(int(div.get('class')[0].split('_')[-1]))
    print('double', start_race_double)

    # get starting race no of Treble
    url = "https://bet.hkjc.com/racing/pages/odds_tbl.aspx?lang=en"
    r = request(url)
    soup = BeautifulSoup(r, "html.parser")

    divs = soup.find("div", attrs={"class": 'racebg'}).find_all("div", attrs={"class": re.compile('raceNoO')})
    start_race_treble = []
    for div in divs:
        start_race_treble.append(int(div.get('class')[0].split('_')[-1]))
    print('treble', start_race_treble)

    # get starting race no of Double Trio
    url = "https://bet.hkjc.com/racing/pages/odds_dt.aspx?lang=en"
    r = request(url)
    soup = BeautifulSoup(r, "html.parser")

    divs = soup.find_all("div", attrs={"class": re.compile('raceNoO')})
    start_race_dt = []
    for div in divs:
        start_race_dt.append(int(div.get('class')[0].split('_')[-1]))
    print('double trio', start_race_dt)

    # get starting race no of Trio
    url = "https://bet.hkjc.com/racing/pages/odds_tt.aspx?lang=en"
    r = request(url)
    soup = BeautifulSoup(r, "html.parser")

    start_race_trio = soup.find("div", attrs={"class": re.compile('raceNoOn_')}).get('class')[0].strip()[-1]
    start_race_trio = [int(start_race_trio)]
    print('tt', start_race_trio)

    # get starting race no of Six up
    url = "https://bet.hkjc.com/racing/pages/odds_6up.aspx?lang=en"
    r = request(url)
    soup = BeautifulSoup(r, "html.parser")

    start_race_6up = soup.find("div", attrs={"class": re.compile('raceNoOn_')}).get('class')[0].strip()[-1]
    start_race_6up = [int(start_race_6up)]
    print('6up', start_race_6up)

    # get starting race no of ff
    start_race_all = []
    for n in range(1, total_race_no + 1):
        start_race_all.append(n)
    print('ff', start_race_all)

    return start_race_all, start_race_double, start_race_treble, start_race_dt, start_race_trio, start_race_6up


def get_pools_start_race_no_progressive():
    start_race_progressive_6up, start_race_progressive_tt, start_race_progressive_dt, start_race_progressive_treble = [], [], [], []
    for n in range(1, total_race_no+1):
        if n <= total_race_no - 5:
            start_race_progressive_6up.append(n)
        if n <= total_race_no - 2:
            start_race_progressive_tt.append(n)
        if n <= total_race_no - 1:
            start_race_progressive_dt.append(n)
        if n <= total_race_no - 2:
            start_race_progressive_treble.append(n)

    return start_race_progressive_6up, start_race_progressive_tt, start_race_progressive_dt, start_race_progressive_treble


def get_stop_sell_time_progressive(stop_sell_times):
    time_progressive_6up = stop_sell_times[:-5]
    time_progressive_tt = stop_sell_times[:-2]
    time_progressive_dt = stop_sell_times[:-1]
    time_progressive_treble = stop_sell_times[:-2]

    return time_progressive_6up, time_progressive_tt, time_progressive_dt, time_progressive_treble


def get_stop_sell_time(start_race_double, start_race_treble, start_race_dt, start_race_tt, start_race_6up):
    stop_sell_times = []
    for race_no in range(1, total_race_no + 1):
        url = f"https://bet.hkjc.com/racing/index.aspx?lang=en&raceno={race_no}"
        r = request(url)
        soup = BeautifulSoup(r, "html.parser")
        divs = soup.select("div.bodyMainOddsTable.content div div span nobr")
        for div in divs:
            if ":" in div.text:
                hour = int(div.text.split(':')[0])  # '18:45' --> 18
                minute = int(div.text.split(':')[1])  # '18:45' --> 45
                # print(hour, ':', minute)
                today = date.today()
                # datetime(year, month, day, hour, minute, second, microsecond)
                race_stop_sell_time = datetime(today.year, today.month, today.day, hour, minute, 0, 0)  # @@
                stop_sell_times.append(race_stop_sell_time)
    # @@
    # stop_sell_times = [datetime(2021, 4, 21, 17, 27 + 0, 30, 0), datetime(2021, 4, 21, 17, 27 + 1, 0, 0),
    #                    datetime(2021, 4, 21, 17, 27 + 2, 0, 0), datetime(2021, 4, 21, 17, 27 + 3, 0, 0),
    #                    datetime(2021, 4, 21, 17, 27 + 4, 0, 0), datetime(2021, 4, 21, 17, 27 + 5, 0, 0),
    #                    datetime(2021, 4, 21, 17, 27 + 6, 0, 0), datetime(2021, 4, 21, 17, 27 + 7, 0, 0),
    #                    datetime(2021, 4, 21, 17, 27 + 8, 0, 0)]

    time_double, time_treble, time_dt = [], [], []
    for idx, val in enumerate(start_race_double):
        time_double.append(stop_sell_times[int(val)])
    for idx, val in enumerate(start_race_treble):
        time_treble.append(stop_sell_times[int(val)])
    for idx, val in enumerate(start_race_dt):
        time_dt.append(stop_sell_times[int(val)])
    time_tt = [
        stop_sell_times[start_race_tt[0] - 1] if len(start_race_tt) > 0 else stop_sell_times[-1] + timedelta(hours=8)]
    time_6up = [
        stop_sell_times[start_race_6up[0] - 1] if len(start_race_6up) > 0 else stop_sell_times[-1] + timedelta(hours=8)]
    time_ff = stop_sell_times
    time_win = stop_sell_times
    time_jkc = stop_sell_times[-2]

    time_last_race = stop_sell_times[-1]

    return stop_sell_times, time_tt, time_6up, time_double, time_treble, time_dt, time_ff, time_win, time_jkc, time_last_race


def get_jackpots(start_race_no_dt, start_race_no_trio, start_race_no_6up):
    print('getting jackpots.....')
    # tt
    url = 'https://bet.hkjc.com/racing/pages/odds_tt.aspx?lang=en'
    r = request(url)
    soup = BeautifulSoup(r, 'html.parser')

    jackpot_tags = soup.find_all("td", {"class": "yellowBar"})
    if len(jackpot_tags) > 1:
        jackpot_tt_list = []
        original_str = jackpot_tags[1].text.strip()
        replacing_word_list = ['\r', '\n', '\t', ',', '-', '$', ' ', ':', 'Jackpot']
        to_be_replaced = ''
        try:
            jackpot_tt_text = replacement(original_str, replacing_word_list, to_be_replaced)
            if len(jackpot_tt_text) > 0:
                jackpot_tt = int(jackpot_tt_text)
                jackpot_tt_list.append([start_race_no_trio[0], jackpot_tt])
            else:
                jackpot_tt_list = []
        except Exception as e:
            print('tt exception: ', e)
            jackpot_tt_list = []
    print('jackpot_tt_list', jackpot_tt_list)

    # 6up
    url = 'https://bet.hkjc.com/racing/pages/odds_6up.aspx?lang=en'
    r = request(url)
    soup = BeautifulSoup(r, 'html.parser')

    jackpot_tags = soup.find_all("td", {"class": "yellowBar"})
    if len(jackpot_tags) > 1:
        jackpot_6up_list = []
        original_str = jackpot_tags[1].text.strip()
        replacing_word_list = ['\r', '\n', '\t', ',', '$', ' ', ':', '-', 'Six', 'Win', 'Bonus', 'Jackpot']
        to_be_replaced = ''
        try:
            jackpot_6up_text = replacement(original_str, replacing_word_list, to_be_replaced)
            if len(jackpot_6up_text) > 0:
                jackpot_6up = int(jackpot_6up_text)
                jackpot_6up_list.append([start_race_no_6up[0], jackpot_6up])
            else:
                jackpot_6up_list = []
        except Exception as e:
            print('6up exception: ', e)
            jackpot_6up_list = []
    print('jackpot_6up_list', jackpot_6up_list)

    # First 4
    jackpot_ff_list = []
    for i in range(1, total_race_no + 1):
        race_no = i
        url = f'https://bet.hkjc.com/racing/pages/odds_ff.aspx?lang=en&raceno={i}'
        r = request(url)
        soup = BeautifulSoup(r, 'html.parser')

        jackpot_tags = soup.find_all("td", {"class": "yellowBar"})
        if len(jackpot_tags) > 1:
            original_str = jackpot_tags[1].text.strip().split('$')[-1]
            replacing_word_list = ['\r', '\n', '\t', ',', '$', ' ', ':']
            to_be_replaced = ''

            jackpot_ff = int(replacement(original_str, replacing_word_list, to_be_replaced))
            if jackpot_ff > 0:
                # print('ff', race_no, jackpot_ff)
                jackpot_ff_list.append([race_no, jackpot_ff])
    print('jackpot_ff_list', jackpot_ff_list)

    # double trio
    jackpot_dt_list = []
    for race_no in start_race_no_dt:
        url = f'https://bet.hkjc.com/racing/pages/odds_dt.aspx?lang=en&raceno={race_no}'
        r = request(url)
        soup = BeautifulSoup(r, 'html.parser')

        jackpot_tags = soup.find_all("td", {"class": "yellowBar"})
        if len(jackpot_tags) > 1:
            original_str = jackpot_tags[1].text.strip().split('$')[-1]
            replacing_word_list = ['\r', '\n', '\t', ',', '$', ' ', ':']
            to_be_replaced = ''

            try:
                jackpot_dt = int(replacement(original_str, replacing_word_list, to_be_replaced))
                # print('dt', race_no, jackpot_dt)
                jackpot_dt_list.append([race_no, jackpot_dt])
            except Exception as e:
                continue
    print('jackpot_dt_list', jackpot_dt_list)

    return jackpot_tt_list, jackpot_6up_list, jackpot_ff_list, jackpot_dt_list


def write_jackpots(pool_type, jackpot_list):
    if jackpot_list:
        msg = ''
        for i in range(len(jackpot_list)):
            start_race_no = jackpot_list[i][0]
            # start_race_no = jackpot_list[i][0][0]  #'int' object is not subscriptable
            jackpot = jackpot_list[i][1]

            msg += f'{race_day},{start_race_no},{pool_type},{jackpot},{venue}\n'
        # output_path = "D:\\Downloads\\1 Archive\\3 HKJC\Racing\\"
        filename = 'history_jackpot.txt'
        write_file(msg, output_path + filename)


def write_all_jackpots(jackpot_tt_list, jackpot_6up_list, jackpot_ff_list, jackpot_dt_list):
    print('writing jackpots.....')
    write_jackpots('ff', jackpot_ff_list)
    write_jackpots('dt', jackpot_dt_list)
    write_jackpots('tt', jackpot_tt_list)
    write_jackpots('qtt', jackpot_6up_list)


def remove_odds_checker_links():
    file = open("odds_checker_links.txt", "r+")
    file.truncate(0)
    file.close()
    print('cleared odds checker links')


def read_odds_checker_links():
    with open('odds_checker_links.txt') as f:
        content = f.readlines()
    list_odds_checker = [x.strip() for x in content]
    # print(list_odds_checker)
    return list_odds_checker


def write_odds_checker(url, race_no, filename):
    path = "D:\\Downloads\\1 Archive\\6 Software\\Tutorial_Python\\chromedriver.exe"
    # url = f'https://www.oddschecker.com/horse-racing/roscommon/19:40/winner'
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(executable_path=path, options=options)
    driver.get(url)
    driver.implicitly_wait(4)
    soup = bs(driver.page_source, "html.parser")
    # print(soup.prettify())
    tbody = soup.find('tbody', attrs={"id": "t1"})
    trs = tbody.find_all('tr')
    # all_list = []
    df = pd.DataFrame([])
    for tr in trs:
        tds = tr.find_all('td')
        row_list = []
        counter = 0
        column_name = []
        for td in tds:
            temp_str = td.text
            odds = 0
            try:
                if '/' in temp_str:
                    odds = float(temp_str.split('/')[0])/float(temp_str.split('/')[1])+1
                else:
                    odds = float(temp_str)+1
                if odds > 0:
                    row_list.append(odds)
                    column_name.append(f'bookie_{counter - 1}')
                    counter += 1
            except:
                if len(temp_str) > 0:
                    row_list.append(temp_str)
                    column_name.append(f'bookie_{counter - 1}')
                    counter += 1
        print(row_list)
        # column_name[0] = 'horse_num'
        # column_name[1] = 'horse_name'
        # print(column_name)
        # df_temp = pd.DataFrame([row_list], columns=[column_name])
        max_odds = 0
        for odds in row_list[2:]:
            try:
                if odds > max_odds:
                    max_odds = odds
            except:
                continue
        row_list_updated = [row_list[0], row_list[1], max_odds]
        df_temp = pd.DataFrame([row_list_updated], columns=['horse_num', 'horse_name', 'max_odds'])
        df = df.append(df_temp)
        # all_list.append(row_list)
    print('#' * 100)
    # print(all_list)
    driver.quit()
    df['date'] = datetime.today().date()
    df['race_no'] = race_no
    df['time'] = datetime.now()
    df = df[['date', 'race_no', 'time', 'horse_num', 'horse_name', 'max_odds']]
    pd.set_option('display.max_columns', None)
    print(f'odds checker: {race_no}, url: {url}')
    print(df)
    df_main = pd.read_csv(f'{filename}.csv')
    df_main = df_main.append(df)
    df_main.to_csv(f'{filename}.csv', index=False)


def get_odds_checker_links(venue):
    places = 'sha-tin' if venue == 'ST' else 'happy-valley'
    url = f'https://www.oddschecker.com/horse-racing/{places}'  # @@

    path = "D:\\Downloads\\1 Archive\\6 Software\\Tutorial_Python\\chromedriver.exe"
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(executable_path=path, options=options)
    driver.get(url)
    driver.implicitly_wait(4)
    soup = bs(driver.page_source, "html.parser")
    time.sleep(1)
    # print(soup.prettify())
    a = soup.find_all('a')
    # for element in a:
    #     if venue in element['href']:
    #         print(element['href'])
    # parent_link = f'/horse-racing/{places}/'
    parent_link = f'/horse-racing/{places}/'  # @@
    links = []
    for item in a:
        partial_link = item['href']
        if parent_link in partial_link and partial_link not in links:
            links.append('https://www.oddschecker.com' + partial_link)
    links = list(dict.fromkeys(links))  # deduplicate
    driver.quit()

    f = open('odds_checker_links.txt', 'w', encoding="utf-8")
    for link in links:
        print(link)
        temp_str = link + '\n' if link != links[-1] else link
        f.write(temp_str)
    f.close()


def check_odds_checker_health():
    urls = read_odds_checker_links()
    for url in urls:
        print('health check - odds checker', url)
        path = "D:\\Downloads\\1 Archive\\6 Software\\Tutorial_Python\\chromedriver.exe"
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(executable_path=path, options=options)
        driver.get(url)
        driver.implicitly_wait(4)
        soup = bs(driver.page_source, "html.parser")
        if 'QuickBet' not in soup.text:
            msg = f'problem in odds checker\n{url}'
            print(msg, '\n')
            print(soup.text)
            easygui.msgbox(msg, title='Error')
        driver.quit()
    print('odds checker health check completed.............')


def check_write_odds(bInplay_boolean, times, odds_type, pool_type, seconds_before, start_race_list, race_range):
    if any(bInplay_boolean):
        for idx, val in enumerate(times):
            if bInplay_boolean[idx] and times[idx] - timedelta(seconds=seconds_before) <= datetime.now():
                bInplay_boolean[idx] = False
                print(pool_type)
                for race_no in range(start_race_list[idx], start_race_list[idx] + race_range):
                    if pool_type == 'inplay_win':
                        print('inplay_win', ' odds checker :', race_no)
                        urls = read_odds_checker_links()
                        if len(urls) > 0:
                            write_odds_checker(urls[race_no - 1], race_no, 'odds_checker_odds_win')
                    else:
                        write_odds(odds_type, race_no, pool_type)  # non inplay_win & non progressive_sixup

                    if pool_type == 'progressive_sixup':
                        print('progressive_sixup', ' odds checker :', race_no)
                        urls = read_odds_checker_links()
                        if len(urls) > 0:
                            write_odds_checker(urls[race_no - 1], race_no, 'odds_checker_odds_6up')
    return bInplay_boolean


def write_odds(pool, race_no, inplay_type):
    if inplay_type != 'final':
        filename = output_path + f'history_{inplay_type}.txt'

        url = f"https://bet.hkjc.com/racing/getJSON.aspx?type={pool}&date={race_day}&venue={venue}&raceno={race_no}"
        r = request(url)
        soup = BeautifulSoup(r, "html.parser")
        msg = f'{race_day},{venue},{race_no},{datetime.now()},{soup.prettify()}'
        write_file(msg, filename)
        # {"OUT":"150110@@@;1=5.4=0;2=4.2=1;3=12=0;4=12=0;5=7.8=0;6=84=0;7=39=0;8=48=0;9=13=0;10=28=0;11=20=0;12=62=0;13=7.7=0;14=6.8=0"}
    else:
        # final odds
        total_race_no = race_no
        # get pools:
        pools_list = ["pooltot", "win", "pla", "tribank", "tri", "qin", "qpl", "fct", "dbl", "tcebank", "tceinv",
                      "fftop",
                      "ffbank", "ff", "qttbank", "cwaodds", "cwbodds", "cwcodds", "raceres"]
        for pool in pools_list:
            filename = output_path + f'history_{pool}.txt'
            for race_no in range(1, total_race_no + 1):
                url = f'https://bet.hkjc.com/racing/getJSON.aspx?type={pool}&date={race_day}&venue={venue}&raceno={race_no}'
                r = request(url)
                soup = BeautifulSoup(r, "html.parser")
                msg = f'{race_day},{venue},{race_no},{soup.prettify()}'
                write_file(msg, filename)

        # get everything XML
        # url = "https://iosbsinfo02.hkjc.com/infoA/AOSBS/HR_GetInfo.ashx?QT=HR_ODDS_ALL&Race=*&Venue=*&Result=1&Dividend=1&JTC=1&JKC=1&Lang=zh-HK"
        # r = request(url)
        # soup = BeautifulSoup(r, "html.parser", from_encoding='utf-8')
        # filename_with_path = output_path + "race_day\\{:%Y-%m-%d}.txt".format(race_day)
        # print(filename_with_path)
        # f = open(filename_with_path, 'w', encoding="utf-8")
        # f.write(soup.prettify())
        # f.close()


def initialize_boolean(start_race_double, start_race_treble, start_race_dt):
    bMeeting, bInplay_tt, bInplay_6up, bInplay_jkc = True, [True], [True], True
    bInplay_double, bInplay_treble, bInplay_dt, bInplay_ff, bInplay_win = [], [], [], [], []
    for n in range(len(start_race_double)):
        bInplay_double.append(True)
    for n in range(len(start_race_treble)):
        bInplay_treble.append(True)
    for n in range(len(start_race_dt)):
        bInplay_dt.append(True)
    for n in range(total_race_no):
        bInplay_ff.append(True)
        bInplay_win.append(True)

    return bMeeting, bInplay_tt, bInplay_6up, bInplay_double, bInplay_treble, bInplay_dt, bInplay_ff, bInplay_win, bInplay_jkc


def initialize_boolean_progressive():
    bProgressive_6up, bProgressive_tt, bProgressive_dt, bProgressive_treble = [], [], [], []
    for n in range(1, total_race_no+1):
        if n <= total_race_no - 5:
            bProgressive_6up.append(True)
        if n <= total_race_no - 2:
            bProgressive_tt.append(True)
        if n <= total_race_no - 1:
            bProgressive_dt.append(True)
        if n <= total_race_no - 2:
            bProgressive_treble.append(True)
    return bProgressive_6up, bProgressive_tt, bProgressive_dt, bProgressive_treble


def check_start_time_within_2_hours(stop_sell_times):
    if stop_sell_times[0] <= datetime.now() + timedelta(minutes=2 * 60):
        while datetime.now() < stop_sell_times[0] - timedelta(minutes=15):
            print('sleeping until start sell: time diff: ', stop_sell_times[0] - datetime.now())
            time.sleep(300)
    else:
        print('over 2 hours before start sell, stop program..sleep 60s')
        time.sleep(60)
        sys.exit()


def main():
    if race_day == date.today() + timedelta(days=0) and venue in ('ST', 'HV'):  # @@
        try:
            print(f'Today is race day! [{venue}]')
            for _ in range(3):
                winsound.PlaySound("hey", winsound.SND_FILENAME)
            print('update odds checker links')
            print('https://www.oddschecker.com/horse-racing/')
            get_odds_checker_links(venue)
            check_odds_checker_health()

            start_race_all, start_race_double, start_race_treble, start_race_dt, start_race_tt, start_race_6up = get_pools_start_race_no()
            start_race_progressive_6up, start_race_progressive_tt, start_race_progressive_dt, start_race_progressive_treble = get_pools_start_race_no_progressive()

            # program blocker: check starting time within 2 hour
            stop_sell_times, time_tt, time_6up, time_double, time_treble, time_dt, time_ff, time_win, time_jkc, time_last_race = get_stop_sell_time(start_race_double, start_race_treble, start_race_dt, start_race_tt, start_race_6up)
            print('stop_sell_times', stop_sell_times)
            # time.sleep(500)
            check_start_time_within_2_hours(stop_sell_times)

            # update jackpots
            jackpot_tt_list, jackpot_6up_list, jackpot_ff_list, jackpot_dt_list = get_jackpots(start_race_dt, start_race_tt, start_race_6up)
            write_all_jackpots(jackpot_tt_list, jackpot_6up_list, jackpot_ff_list, jackpot_dt_list)

            msg_jkc_previous = ""
            time_counter = 0

            bMeeting, bInplay_tt, bInplay_6up, bInplay_double, bInplay_treble, bInplay_dt, bInplay_ff, bInplay_win, bInplay_jkc = initialize_boolean(start_race_double, start_race_treble, start_race_dt)
            bProgressive_6up, bProgressive_tt, bProgressive_dt, bProgressive_treble = initialize_boolean_progressive()
            while bMeeting or any(bInplay_tt) or any(bInplay_6up) or bInplay_jkc or any(bInplay_double) or any(bInplay_treble) or any(bInplay_dt) or any(bInplay_ff) or any(bInplay_win) or any(bProgressive_6up) or any(bProgressive_tt) or any(bProgressive_dt) or any(bProgressive_treble):
                print(f'sleep 1s...time_counter: {time_counter}', end="\r")
                time.sleep(1)
                time_counter += 1
                if time_counter == 1:
                    if bInplay_ff:  # check meeting not yet ended
                        stop_sell_times, time_tt, time_6up, time_double, time_treble, time_dt, time_ff, time_win, time_jkc, time_last_race = get_stop_sell_time(start_race_double, start_race_treble, start_race_dt, start_race_tt, start_race_6up)
                        time_progressive_6up, time_progressive_tt, time_progressive_dt, time_progressive_treble = get_stop_sell_time_progressive(stop_sell_times)
                        print(stop_sell_times)
                elif time_counter >= 5 * 60:  # refresh time interval for jkc and stop sell time, 5 mins
                    time_counter = 0
                    if bInplay_jkc:
                        if time_jkc > datetime.now():
                            url = f"https://bet.hkjc.com/racing/getJSON.aspx?type=jkc&date={race_day}&venue={venue}"
                            r = request(url)
                            soup = BeautifulSoup(r, "html.parser")
                            msg = soup.prettify()
                            if msg != msg_jkc_previous:
                                msg_jkc_previous = msg
                                write_odds('jkc', 0, 'inplay_jkc')
                        else:
                            bInplay_jkc = False

                # write_inplay_odds()
                bInplay_6up = check_write_odds(bInplay_6up, time_6up, 'win', 'inplay_sixup', 60, start_race_6up, 6)
                bInplay_tt = check_write_odds(bInplay_tt, time_tt, 'tri', 'inplay_tt', 60, start_race_tt, 3)
                bInplay_dt = check_write_odds(bInplay_dt, time_dt, 'tri', 'inplay_dt', 45, start_race_dt, 2)
                bInplay_treble = check_write_odds(bInplay_treble, time_treble, 'win', 'inplay_treble', 30, start_race_treble, 3)
                bInplay_double = check_write_odds(bInplay_double, time_double, 'dbl', 'inplay_dbl', 30, start_race_double, 1)
                bInplay_ff = check_write_odds(bInplay_ff, time_ff, 'ff', 'inplay_ff', 45, start_race_all, 1)
                bInplay_win = check_write_odds(bInplay_win, time_win, 'win', 'inplay_win', 45, start_race_all, 1)  # odds checker

                bProgressive_tt = check_write_odds(bProgressive_tt, time_progressive_tt, 'tri', 'progressive_tt', 60, start_race_progressive_tt, 3)
                bProgressive_dt = check_write_odds(bProgressive_dt, time_progressive_dt, 'tri', 'progressive_dt', 45, start_race_progressive_dt, 2)
                bProgressive_treble = check_write_odds(bProgressive_treble, time_progressive_treble, 'win', 'progressive_treble', 30, start_race_progressive_treble, 3)
                bProgressive_6up = check_write_odds(bProgressive_6up, time_progressive_6up, 'win', 'progressive_sixup', 60, start_race_progressive_6up, 6)   # include odds checker

                # write final odds, post meeting after 20 min
                if bMeeting and time_last_race + timedelta(minutes=20) <= datetime.now():
                    bMeeting = False
                    print('write final odds......')
                    write_odds('', total_race_no, "final")
                    remove_odds_checker_links()
            print('Meeting ended')
            easygui.msgbox('Meeting ended', title='Meeting ended')

        except Exception as e:
            print(e)


if __name__ == "__main__":
    output_path = "D:\\Downloads\\1 Archive\\6 Software\\Tutorial_Python\\betting\\racing\\"
    # output_path = "D:\\Downloads\\1 Archive\\3 HKJC\Racing\\"
    race_day, venue, total_race_no = get_current_race_day_venue_race_no()
    main()