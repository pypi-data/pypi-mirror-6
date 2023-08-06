#coding=utf-8

import sdxf

'''生成绘图空间'''
d = sdxf.Drawing()



'''设置图层名字和颜色'''
#可以是已有图册
#在没有设置图层时候，直接添加到一个新名字的图层
#图层将以默认颜色与新名字来添加新的图层
#Layers are used to organize entities.
#Layers can be assigned colors to make drawings easier to read.
#An entity can be assigned to a new layer on the fly, without explicitly defining the layer first.
#Layer(name="layer_name",color=3)
d.layers.append( sdxf.Layer(name="layer1", color=3) )



'''块blocks'''
#Blocks are reusable symbols.
#A block is defined once and can then be appended to the drawing using the Insert entity.
#A block can be inserted multiple times into a drawing, at different points.
#命名block
b = sdxf.Block('test_block')
#添加元素进入block
b.append( sdxf.Text('Hello, I am a block!', color = 2 ) )
#将block添加到绘图空间的block预插入集合中去
d.blocks.append(b)
#在绘图空间中使用block
d.append( sdxf.Insert('test_block', point=(3,3), cols=5, rows=5, colspacing=32, rowspacing=15) )




'''添加图元'''

#Text(String, point=)
'''Text'''
d.append( sdxf.Text('Hello World!',point=(3,0), layer="layer1") )


#Line(points = [ point1_tuple, point2_tuple ] )
'''Line'''
d.append( sdxf.Line(points=[(0, 0), (1, 1)], layer="layer2") )


#center (x, y, z) - The center of the circle from which the arc is to be taken. Z is optional.
#radius - The radius from the center to the arc
#startAngle - The angle, in degrees, for the start of the arc.
#endAngle - The angle, in degrees, for the end of the arc
#Arc(center=(3,0),radius=2,startAngle=0,endAngle=90)
'''Arc'''
d.append( sdxf.Arc( (3,0), 5, 45, 90, layer="layer_arc") )


#Draws a circle
#center (x,y,z) - the center of the circle. Z is optional.
#radius - the radius of the circle
#Circle( center=(3,0), radius=3 )
'''Circle'''
d.append( sdxf.Circle( (3,0), 3, layer="layer_arc") )


#Insert
#Blocks are added to a file using the Insert entity.
#The block must be added to the Blocks table before it can be used.
#name - Block name (defined when the block was added to the Blocks table)
#point - Insertion point (x,y,z) to add the block
#xscale - x scale factor; optional, defaults to 1
#yscale - y scale factor; optional, defaults to 1
#zscale - z scale factor; optional, defaults to 1
#cols - column count; optional, defaults to 1
#colspacing - column spacing; optional, defaults to 0
#rows - row count; optional, defaults to 1
#rowspacing - row spacing; optional, defaults to 0
#rotation - rotation angle; optional, defaults to 0
#例子详见blocks章节
'''Insert'''


#LwPolyLine/PolyLine
#开源库中的LwPolyLine是错的
#开源库中的PolyLine是假的
#对PolyLine进行了重写，然后让LwPolyLine等同于PolyLine
#建议只使用PolyLine
#flag为1则是闭合多段线
#如果不传入flag,flag默认为0
'''PolyLine'''
linePoints = [ (0,0), (1,3), (1,0), (2,2) ]
d.append( sdxf.LwPolyLine( points=linePoints, flag=1, color=3, layer="layer_lw" ) )


'''保存成dxf格式的文件'''
#saveas("文件的路径和名称")
d.saveas( "test.dxf" )