def ascii_percentage_bar(self,percentage:float,width:int=20)->str:
    bar = '█' * int(percentage * width)
    bar += '░' * (width - len(bar))
    return bar


print(ascii_percentage_bar(None,0.5))