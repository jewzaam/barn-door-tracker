// super simple cube to use for custom support in cura (for the bearings)

/* [From tracker.scad] */

hinge_thickness = 5;

bearing_diameter = 22.1;

bearing_height = 7;

/* [Hidden] */

$fn=200;

// subtract some material so we don't get clipping outside of the main part in cura when using this model as a support
hinge_housing_diameter=bearing_diameter+hinge_thickness*2-hinge_thickness/2;

hull()
{
    translate([0,0,hinge_housing_diameter/2])
    rotate([90,0,0])
    cylinder(d=hinge_housing_diameter,h=bearing_height,center=true);
    
    cube([hinge_housing_diameter,bearing_height,1],center=true);
}