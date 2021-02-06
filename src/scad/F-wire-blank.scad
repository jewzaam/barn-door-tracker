xyz=[2.5,2.5,12];
thickness=0.6;

difference()
{
    cube(xyz,center=true);
    cube(xyz+[-thickness*2,-thickness*2,thickness*2],center=true);
}