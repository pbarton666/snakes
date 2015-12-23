def stg2tup(stg):
    "convert a sting like '123,456,789' to a tuple like (123, 456, 789)"
    return tuple([int(i) for i in stg.split(',')] )

def tup2stg(tup):
    "convert a tuple like (123, 456, 789) to a string like '123, 456, 789'"
    return  ', '.join([str(i) for i in tup])

if __name__=='__main__':
    assert stg2tup('123, 456, 789')==(123, 456, 789)
    assert stg2tup('123,456,789')==(123, 456, 789)
    assert tup2stg((123, 456, 789))=='123, 456, 789'
    print('Yea! Tests passed')