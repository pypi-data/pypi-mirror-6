def pretty_print(headers, data, size = 20):
    print
    header_string = ''
    underline_string = ''
    for head in headers:
        header_string += head.ljust(size)
        underline_string += (('-' * len(head)).ljust(size))
    
    print header_string
    print underline_string
    
    data_string = ''
    for d in data:
        for f in d:
            data_string += f.ljust(size)
            
        print data_string
        data_string = ''
