def foo(number_of_pages):
    print("=====%s====" % number_of_pages)
    for i in range(int(number_of_pages / 10) + 1):
        frompage = (i * 10) + 1
        topage = min((i + 1) * 10, number_of_pages)
        if frompage <= topage:
            print("From %s to %s" % (frompage, topage))

foo(9)
foo(10)
foo(11)
foo(19)
foo(20)
foo(21)
