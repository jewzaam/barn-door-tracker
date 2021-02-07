// quick case and button for 5-way navigation switch
// https://www.adafruit.com/product/504
// adafruit product id 504


switch_hole_d=5.9;


switch_base_xyz=[10.5,10.5,3.7];

case_body_d=20;
case_hole_d=9;
case_body_h=80;

thickness=2;

$fn=200;

/*

Create a case that can be held in hand for use.  The body of the case is a cylinder.  It has a ledge for the switch to sit on and a hole big enough for wiring to fit through.  A lit fits over the switch once it's resting on the ledge
*/

difference()
{
    cylinder(d=case_body_d,h=case_body_h,center=true);
    
cube([switch_base_xyz[0],switch_base_xyz[1],case_body_h+10],center=true);    
}

