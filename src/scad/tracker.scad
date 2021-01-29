part = "both"; // [bottom:"Bottom",top:"Top",both:"Top and Bottom",test:"Tester"]

/* [Tracker] */

// how far away the center of the rod is from the hinge
tracker_radius = 200;

tracker_extra_length=20;

hinge_thickness = 5;

// how wide the bolt at the hinge is
hinge_bolt_diameter = 8;

// how wide the hinge is, probably a bit shorter than your bolt length to allow for washers and nut
hinge_length = 100;

// the hinge bearing outer diameter
bearing_diameter = 22.1;

// height of the bearing
bearing_height = 7;

// diameter of rod/bolt/whatever that attaches to the tripod
tripod_bolt_diameter = 7;

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

// how far the shaft is offset from the center of the stepper
stepper_motor_to_shaft_diameter = 7.25;

/* [Constants] */

hinge_housing_diameter=bearing_diameter+hinge_thickness*2;
tracker_thickness=hinge_housing_diameter/2-2;
tracker_length=bearing_diameter/2+hinge_thickness+tracker_radius+rod_diameter/2;
top_width=hinge_length-bearing_height*2-2;
camera_bolt_housing_diameter=camera_bolt_diameter+hinge_thickness;
hinge_bolt_housing_diameter=hinge_bolt_diameter+hinge_thickness;


/* [Shapes] */

$fn = 100;

module cut_rod_hole_bottom()
{
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
}

module cut_tripod_hole()
{
    translate([0,0,-1])
    cylinder(d=tripod_bolt_diameter,h=tracker_thickness*2);
}

module part_bearing_housing()
{
    difference()
    {
        hull()
        {
            // the bearing housing
            translate([hinge_housing_diameter/2,0,hinge_housing_diameter/2])
            rotate([-90,0,0])
            cylinder(d=hinge_housing_diameter,h=hinge_length/2);
            
            // hull w/ a section of the bottom for some nice shapes
            translate([hinge_housing_diameter,0,0])
            cube([tracker_length*0.2,hinge_length/2,tracker_thickness]);
        }
        
        // cut out room for the tracker top
        translate([-1,bearing_height,-1])
        cube([tracker_length,hinge_length-bearing_height*2,tracker_thickness+hinge_housing_diameter]);

        // cut out the bearing
        translate([hinge_housing_diameter/2,-1,hinge_housing_diameter/2])
        rotate([-90,0,0])
        cylinder(d=bearing_diameter,h=hinge_length*1.1);
    }
}

module bottom()
{
    union()
    {
        difference()
        {
            // main body
            translate([hinge_housing_diameter,0,0])
            cube([tracker_length+tracker_extra_length-hinge_housing_diameter,hinge_length,tracker_thickness]);
            
            // cut tripod hole
            translate([tracker_balance_x,hinge_length/2,0])
            cut_tripod_hole();
            
            // cut rod hole
            translate([hinge_housing_diameter/2+tracker_radius,hinge_length/2,tracker_thickness+0.1])
            cut_rod_hole_bottom();

            // cut one angled bit
            translate([tracker_balance_x+tracker_extra_length,0,-1])
            rotate([0,0,atan((hinge_length/2-tracker_extra_length)/(tracker_length-tracker_balance_x-tracker_extra_length))])
            mirror([0,1,0])
            cube([tracker_length,hinge_length,tracker_thickness*2]);

            // cut other angled bit
            translate([tracker_balance_x+tracker_extra_length,hinge_length,-1])
            rotate([0,0,-atan((hinge_length/2-tracker_extra_length)/(tracker_length-tracker_balance_x-tracker_extra_length))])
            cube([tracker_length,hinge_length,tracker_thickness*2]);
        }
        
        part_bearing_housing();

        translate([0,hinge_length-bearing_height,0])
        part_bearing_housing();
    }
}

module part_hinge_bolt_housing(h)
{
    rotate([-90,0,0])
    cylinder(d=hinge_bolt_housing_diameter,h=h);
}

module cut_hinge_bolt()
{
    translate([0,-1,0])
    rotate([-90,0,0])
    cylinder(d=hinge_bolt_diameter,h=hinge_length*1.1);
}

module top()
{
    difference()
    {
        union()
        {
            // bolt housing
            translate([hinge_housing_diameter/2,bearing_height,hinge_housing_diameter/2])
            part_hinge_bolt_housing(h=hinge_length-bearing_height*2);
            
            // main body
            translate([(hinge_housing_diameter-hinge_bolt_diameter-hinge_thickness)/2,(hinge_length-top_width)/2,hinge_housing_diameter/2])
            cube([tracker_length+tracker_extra_length-(hinge_housing_diameter-hinge_bolt_diameter-hinge_thickness)/2,top_width,hinge_housing_diameter/2]);
            
            // camera mount housing
            translate([tracker_balance_x,(hinge_length-top_width)/2,hinge_housing_diameter-camera_bolt_housing_diameter/2])
            part_camera_bolt_housing();
        }
        
        // cut out the hinge bolt
        translate([hinge_housing_diameter/2,-1,tracker_thickness*1.2])
        cut_hinge_bolt();
        
        // cut rod hole
        translate([hinge_housing_diameter/2+tracker_radius,hinge_length/2,hinge_housing_diameter/4])
        cut_rod_hole_top();
        
        // cut camera mount rod
        translate([tracker_balance_x,0,hinge_housing_diameter-camera_bolt_housing_diameter/2])
        cut_camera_bolt();
        
        // cut one angled bit
        translate([tracker_balance_x+tracker_extra_length,0,tracker_thickness])
        rotate([0,0,atan((hinge_length/2-tracker_extra_length)/(tracker_length-tracker_balance_x-tracker_extra_length))])
        mirror([0,1,0])
        cube([tracker_length,top_width,tracker_thickness*2]);

        // cut other angled bit
        translate([tracker_balance_x+tracker_extra_length,hinge_length,tracker_thickness])
        rotate([0,0,-atan((hinge_length/2-tracker_extra_length)/(tracker_length-tracker_balance_x-tracker_extra_length))])
        cube([tracker_length,top_width,tracker_thickness*2]);
    }
}

module cut_rod_hole_top()
{
    translate([0,0,-1])
    cylinder(d=rod_diameter,h=tracker_thickness*2);
}

module part_camera_bolt_housing(h=top_width)
{
    rotate([-90,0,0])
    cylinder(d=camera_bolt_housing_diameter,h=h);
}

module cut_camera_bolt()
{
    translate([0,-1,0])
    rotate([-90,0,0])
    cylinder(d=camera_bolt_diameter,h=hinge_length);
}

module test()
{
    test_x=tracker_length*0.27;
    test_y=max(tripod_bolt_diameter,camera_bolt_diameter)*3;
    
    difference()
    {
        union()
        {
            // bearing OD test
            part_bearing_housing();

            // main block
            translate([hinge_housing_diameter,0,0])
            cube([test_x,test_y,tracker_thickness]);
            
            // camera bolt test
            translate([hinge_housing_diameter+camera_bolt_housing_diameter/2,0,camera_bolt_diameter/2+hinge_thickness/2])
            part_camera_bolt_housing(h=test_y);
            
            // hinge bolt test
            translate([hinge_housing_diameter+camera_bolt_housing_diameter+max(rod_diameter,tripod_bolt_diameter)+rod_diameter*1.5+hinge_bolt_housing_diameter/2,0,hinge_bolt_housing_diameter/2])
            part_hinge_bolt_housing(h=test_y);
        }
        
        // cut camera bolt
        translate([hinge_housing_diameter+camera_bolt_diameter/2+hinge_thickness/2,0,camera_bolt_diameter/2+hinge_thickness/2])
        cut_camera_bolt();
                
        // rod test, top
        translate([hinge_housing_diameter+camera_bolt_housing_diameter+tripod_bolt_diameter/2,test_y-(test_y-bearing_height)*3/4,0])
        cut_rod_hole_top();

        // rod test, bottom
        translate([hinge_housing_diameter+camera_bolt_housing_diameter+max(rod_diameter,tripod_bolt_diameter)+rod_diameter,bearing_height+(test_y-bearing_height)/4,tracker_thickness+0.1])
        rotate([0,0,-90])
        cut_rod_hole_bottom();
        
        // cut hinge bolt
        translate([hinge_housing_diameter+camera_bolt_housing_diameter+max(rod_diameter,tripod_bolt_diameter)+rod_diameter*1.5+hinge_bolt_housing_diameter/2,0,hinge_bolt_housing_diameter/2])
        cut_hinge_bolt();
        
        // tripod bolt test
        translate([hinge_housing_diameter+camera_bolt_housing_diameter+max(rod_diameter,tripod_bolt_diameter)+rod_diameter*1.5+hinge_bolt_housing_diameter+tripod_bolt_diameter/2,bearing_height+(test_y-bearing_height)*1/4,0])
        cut_tripod_hole();

        // stepper motor test
        translate([hinge_housing_diameter+camera_bolt_housing_diameter+tripod_bolt_diameter/2,test_y-stepper_hole_diameter,0])
        cut_stepper_motor();
    }
    
    
    
    // scope mount..
}

module cut_stepper_motor()
{
    // bolts
    translate([0,0,-1])
    {
        cylinder(d=stepper_hole_diameter,h=tracker_thickness*2);
        translate([stepper_hole_distance,0,0])
        cylinder(d=stepper_hole_diameter,h=tracker_thickness*2);
    }
    
    // gear
    translate([stepper_hole_distance/2,stepper_motor_to_shaft_diameter,-1])
    cylinder(d=stepper_gear_diameter,h=stepper_motor_to_gear_height);
}

if (part == "top") {
    top();
} else if (part == "bottom") {
    bottom();
} else if (part == "both") {
    top();
    bottom();
} else if (part == "test") {
    test();
}
