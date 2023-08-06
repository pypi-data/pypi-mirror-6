from datetime import *


# 입력된 년 월의 달력을 출력해주는 함수
def print_cal(yyyy, mm, sunday_start=True) :

    ### 날짜 계산 ###
    input_date = date(yyyy, mm, 1)

    # 년 / 월 / 일 분리
    s = str(input_date).split('-')
    print("\n\t\t  ", s[0], "년", s[1], "월\n")

    year = int(s[0])
    month = int(s[1])

    chk = 0     # 플래그 chk
    day = 31    # 한달에 며칠있는지 검사하기 위한 while
    while chk == 0 :
        try :
            temp = date(year, month, day)
            chk = 1
        except ValueError :
            day = day - 1

    # 요일을 정수값으로 ==> 월요일 0 ~ 일요일 6
    week_day = date.weekday(date(year, month, 1))

    if sunday_start :
        print_sunday(day, week_day + 1)
    else :
        print_monday(day, week_day)



# 한 주의 시작이 일요일
def print_sunday(day, week_day) :

    ### 달력 출력 시작 ###
    print("일\t월\t화\t수\t목\t금\t토")

    # 1일의 위치 잡아주기
    cnt = 0
    while cnt != week_day :
        print("\t", end="")
        cnt = cnt + 1

    # 달력 출력
    cnt = 1
    while cnt <= day :

        print(cnt, "\t", end="")
        cnt = cnt + 1
        week_day = week_day + 1

        # 토요일이면 개행
        if week_day == 7 :
            week_day = 0
            print()



# 한 주의 시작이 월요일
def print_monday(day, week_day) :

    ### 달력 출력 시작 ###
    print("월\t화\t수\t목\t금\t토\t일")

    # 1일의 위치 잡아주기
    cnt = 0
    while cnt != week_day :
        print("\t", end="")
        cnt = cnt + 1

    # 달력 출력
    cnt = 1
    while cnt <= day :

        print(cnt, "\t", end="")
        cnt = cnt + 1
        week_day = week_day + 1

        # 일요일이면 개행
        if week_day == 7 :
            week_day = 0
            print()
