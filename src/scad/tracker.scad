part = "both"; // [bottom:"Bottom",top:"Top",both:"Top and Bottom"]

/* [Tracker] */

// how far away the center of the rod is from the hinge
tracker_radius = 200;

tracker_extra_length=20;

// how wide the bolt at the hinge is
hinge_bolt_diameter = 8;

// how wide the hinge is, probably a bit shorter than your bolt length to allow for washers and nut
hinge_length = 100;

// the hinge bearing outer diameter
bearing_diameter = 22.1;

// height of the bearing
bearing_height = 7;

// diameter of rod/bolt/whatever that attaches to the tripod
tripod_bolt_diameter = 6.35;

// diameter of the rod/bolt/whatever that attaches to the camera
camera_bolt_diameter = 9.6;

// diameter of the threaded rod, add some since the rod must fit through without threading
rod_diameter = 7;

/* [Hidden] */

tracker_balance_x=tracker_radius*0.36;

// might make this not hidden eventually

/* [Stepper] */

stepper_hole_diameter = 3.9;

// distance between center of the 2 mounting holes
stepper_hole_distance = 35;

stepper_motor_diameter = 28;

stepper_motor_height = 21;

// distance from top of motor to the top of usable thread on the gear
stepper_motor_to_gear_height = 22;

stepper_gear_diameter = 20;

/* [Constants] */

hinge_thickness = 5;

/* [Shapes] */

$fn = 100;

module bottom()
{
    a=bearing_diameter+hinge_thickness;
    tracker_thickness=a/2-2;
    x=bearing_diameter/2+hinge_thickness+tracker_radius+rod_diameter/2;

    union()
    {
        difference()
        {
            // main body
            translate([a,0,0])
            cube([x+tracker_extra_length-a,hinge_length,tracker_thickness]);
            
            // cut tripod hole
            translate([tracker_balance_x,hinge_length/2,-1])
            cylinder(d=tripod_bolt_diameter,h=tracker_thickness*2);
            
            
    // cut rod hole
    translate([a/2+tracker_radius,hinge_length/2,tracker_thickness+0.1])
    union()
    {
        translate([0,0,-2])
        cylinder(d=rod_diameter,h=2);

        hull()
        {
            translate([0,0,-2])
            cylinder(d=rod_diameter,h=1);

            translate([0,0,-tracker_thickness*3])
            cylinder(d=rod_diameter,h=1);
            
            rotate([0,35,0])
            translate([0,0,-tracker_thickness*3])
            cylinder(d=rod_diameter,h=1);
        }
    }

            // cut one angled bit
            translate([tracker_balance_x+tracker_extra_length,0,-1])
            rotate([0,0,atan((hinge_length/2-tracker_extra_length)/(x-tracker_balance_x-tracker_extra_length))])
            mirror([0,1,0])
            cube([x,hinge_length,tracker_thickness*2]);

            // cut other angled bit
            translate([tracker_balance_x+tracker_extra_length,hinge_length,-1])
            rotate([0,0,-atan((hinge_length/2-tracker_extra_length)/(x-tracker_balance_x-tracker_extra_length))])
            cube([x,hinge_length,tracker_thickness*2]);
        }
        
        difference()
        {
            hull()
            {
                // the bearing housing
                translate([a/2,0,a/2])
                rotate([-90,0,0])
                cylinder(d=a,h=hinge_length);
                
                // hull w/ a section of the bottom for some nice shapes
                translate([a,0,0])
                cube([x*0.2,hinge_length,tracker_thickness]);
            }
            
            // cut out room for the tracker top
            translate([-1,bearing_height,-1])
            cube([x,hinge_length-bearing_height*2,tracker_thickness+a]);

            // cut out the bearing
            translate([a/2,-1,a/2])
            rotate([-90,0,0])
            cylinder(d=bearing_diameter,h=hinge_length*1.1);
        }
    }
}

module top()
{
    a = bearing_diameter+hinge_thickness;
    tracker_thickness=a/2-2;
    x=bearing_diameter/2+hinge_thickness+tracker_radius+rod_diameter/2;
    b=camera_bolt_diameter+hinge_thickness;
    top_width=hinge_length-bearing_height*2-2;

    difference()
    {
        union()
        {
            // bolt housing
            translate([a/2,bearing_height,a/2])
            rotate([-90,0,0])
            cylinder(d=hinge_bolt_diameter+hinge_thickness,h=hinge_length-bearing_height*2);
            
            // main body
            translate([(a-hinge_bolt_diameter-hinge_thickness)/2,(hinge_length-top_width)/2,a/2])
            cube([x+tracker_extra_length-(a-hinge_bolt_diameter-hinge_thickness)/2,top_width,a/2]);
            
            // camera mount housing
            translate([tracker_balance_x,(hinge_length-top_width)/2,a-b/2])
            rotate([-90,0,0])
            cylinder(d=b,h=top_width);

        }
        
        // cut out the hinge bolt
        translate([a/2,-1,tracker_thickness*1.2])
        rotate([-90,0,0])
        cylinder(d=hinge_bolt_diameter,h=hinge_length*1.1);
        
        // cut rod hole
        translate([a/2+tracker_radius,hinge_length/2,a/4])
        cylinder(d=rod_diameter,h=tracker_thickness*2);
        
        // cut camera mount rod
        translate([tracker_balance_x,0,a-b/2])
        rotate([-90,0,0])
        cylinder(d=camera_bolt_diameter,h=hinge_length);
        
        // cut one angled bit
        translate([tracker_balance_x+tracker_extra_length,0,tracker_thickness])
        rotate([0,0,atan((hinge_length/2-tracker_extra_length)/(x-tracker_balance_x-tracker_extra_length))])
        mirror([0,1,0])
        cube([x,top_width,tracker_thickness*2]);

        // cut other angled bit
        translate([tracker_balance_x+tracker_extra_length,hinge_length,tracker_thickness])
        rotate([0,0,-atan((hinge_length/2-tracker_extra_length)/(x-tracker_balance_x-tracker_extra_length))])
        cube([x,top_width,tracker_thickness*2]);
    }
    

}

if (part == "top") {
    top();
} else if (part == "bottom") {
    bottom();
} else if (part == "both") {
    top();
    bottom();
}
