#This Contains the Area Formulas for Square, Rectangle, Triangle & Circle
def squareArea(x):
	area = x * x
	return area
def rectangleArea(x, y):
	area = x * y
	return area
def triangleArea(x, y):
	area = .5 * x * y
	return area
def circleArea(x):
	import math
	p = math.pi
	area = 2 * p * x
	return area