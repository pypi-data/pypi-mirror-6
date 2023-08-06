def numToWord(number):
    word = []
    if number < 0 or number > 999999:
        print (word)
        raise ValueError("You must type a number between 0 and 999999")
    ones = ["","one","two","three","four","five",
            "six","seven","eight","nine","ten","eleven","twelve",
            "thirteen","fourteen","fifteen","sixteen","seventeen",
            "eighteen","nineteen"]
    if number == 0: return "zero"
    if number > 9 and number < 20:
        return ones[number]
    tens = ["","ten","twenty","thirty","forty","fifty",
            "sixty","seventy","eighty","ninety"]
    word.append(ones[int(str(number)[-1])])
    if number >= 10:
        word.append(tens[int(str(number)[-2])])
    if number >= 100:
        word.append("hundred")
        word.append(ones[int(str(number)[-3])])
    if number >= 1000 and number < 1000000:
        word.append("thousand")
        word.append(numToWord(int(str(number)[:-3])))
    for i,value in enumerate(word):
        if value == '':
            word.pop(i)
    return ' '.join(word[::-1])
