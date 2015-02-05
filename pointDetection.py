import rr
import math
from collections import namedtuple

#Axis m1013 field of view 62.38 degrees in the x direction

c = rr.GetArrayVariable("MEQ_COORDINATES")

#Define named tuples for better self-documentation of our point array
Point = namedtuple('Point', 'x y')
Corners = namedtuple('Corners', 'topRight topLeft bottomLeft bottomRight')

#Function to calculate distance between two points
def distance(p1, p2):
    return math.sqrt( (p1.x - p2.x)**2 + (p1.y - p2.y)**2)
#Calculates arithmetic mean of two numbers
def average(list):
    return sum(list)/len(list)
        
try:
    #TopRight, TopLeft, BottomLeft, BottomRight
    points = Corners(Point(c[0], c[1]), Point(c[2], c[3]), Point(c[4], c[5]), Point(c[6], c[7]))

    #Determine whether the tote is horizontal
    topDistance = distance(points.topRight, points.topLeft)
    bottomDistance = distance(points.bottomRight, points.bottomLeft)
    widthAve = average([topDistance, bottomDistance])

    leftDistance = distance(points.topLeft, points.bottomLeft)
    rightDistance = distance(points.topRight, points.bottomRight)
    heightAve = average([leftDistance, rightDistance])

    if widthAve > heightAve:
        rr.SetVariable("Orientation", "Horizontal")
    else:
        rr.SetVariable("Orientation", "Vertical")

    #Calculate shape center point
    centerX = average ([points.topRight.x, points.topLeft.x, points.bottomRight.x, points.bottomLeft.x])
    centerY = average ([points.topRight.y, points.topLeft.y, points.bottomRight.y, points.bottomLeft.y])
    rr.SetArrayVariable("Center Point", [centerX, centerY])

    #Calculate Angle
    bottomCenter = Point(average([points.bottomLeft.x, points.bottomRight.x]), average([points.bottomLeft.y, points.bottomRight.y]))
    centerPoint = Point(centerX, centerY)
    angle = math.atan2(centerPoint.y - bottomCenter.y, centerPoint.x - bottomCenter.x)
    angle -= math.pi/2

    if widthAve > heightAve:
        if angle < 0:
            angle = math.pi/2 + angle
            bottomCenter = Point(average([points.topRight.x, points.bottomRight.x]), average([points.topRight.y, points.bottomRight.y]))
        else:
            angle = -math.pi/2 + angle
            bottomCenter = Point(average([points.bottomLeft.x, points.topLeft.x]), average([points.bottomLeft.y, points.topLeft.y]))

    rr.SetVariable("Tote Angle", angle)
    rr.SetArrayVariable("Bottom Center Line", list(bottomCenter) + list(centerPoint))

    rr.SetVariable("ToteX", (5.42/math.cos((math.pi/180)*(11+0.078*bottomCenter.y)))*math.tan((math.pi/180)*0.078*(bottomCenter.x-400)))
    rr.SetVariable("ToteY", 5.42*math.tan((math.pi/180)*(11+(0.078*bottomCenter.y))))

    #VERY IMPORTANT: must use list() around the points, or RoboRealms will crash!
    #Probably caused by it getting upset over the tuple being a namedtuple
    rr.SetArrayVariable("Top Right", list(points.topRight))
    rr.SetArrayVariable("Top Left", list(points.topLeft))
    rr.SetArrayVariable("Bottom Left", list(points.bottomLeft))
    rr.SetArrayVariable("Bottom Right", list(points.bottomRight))
    rr.SetVariable("Visible", True)
except (TypeError, IndexError, ZeroDivisionError) as e:
    #This will run when the tote is not visible to the camera
    rr.SetVariable("Visible", False)
