#The function allows to unpack lists of multiple lines#

def unpackList(list_to_work):
	
	for each_item in list_to_work:
		
		if(isinstance(each_item, list)):
			unpackList(each_item)
		else:
			print (each_item)
			
	

