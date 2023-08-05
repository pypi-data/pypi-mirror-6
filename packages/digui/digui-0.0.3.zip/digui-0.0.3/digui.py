# -*- coding: UTF-8 -*-
'''这是一个"nester.py"模块，包含递归方式打印嵌套列表的方法
'''
def p(l,indent=False,level=0):
	for i in l:
		if isinstance(i,list):
			p(i,indent,level+1)
		else:
                        if indent:
                                for x in range(level):
                                        print('\t',end = '')
                        print(i)







			
