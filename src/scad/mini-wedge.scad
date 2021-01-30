// Need something to wedge between parts.  This is a small model that meets that need..


min_z=1;
max_z=3;
x=30;
y=3;


hull()
{
    cube([1,y,min_z]);

    translate([x-1,0,0])
    cube([1,y,max_z]);
}