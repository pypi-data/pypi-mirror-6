
"""이 파일은 sreverse 모듈이며, sreverse() 함수 하나를 제공합니다.
   이 함수는 입력받은 문자열을 뒤집어서 화면에 출력합니다."""
def sreverse(s):
    
    t='' 
    slen = len(s)  # 입력받은 문자열의 길이를 slen에 저장합니다.
    a = 0
    while a < slen:  # while문은 a가 slen보다 크거나 같을때까지 실행됩니다.
        t = s[a]+t   # t 배열에 입력받은 문자열의 문자를 하나하나 넣으면서 a를 증가시킵니다.
        a = a+1
    print(t)         # 최종적으로 배열 t를 출력하게되면 입력받은 문자열이 뒤집어서 출력됩니다.
