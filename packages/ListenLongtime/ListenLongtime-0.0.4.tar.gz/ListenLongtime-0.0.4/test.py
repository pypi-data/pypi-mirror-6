from llt import LongListener

lstr = LongListener()

result = lstr.transcribe(lstr.listen())

print(result)