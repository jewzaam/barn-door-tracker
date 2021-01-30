part = "both"; // [bottom:"Tracker Bottom",top:"Tracker Top",both:"Top and Bottom",bottom_with_gears:"Bottom with Gears",gear43:"Threaded Rod Gear",gear10:"Stepper Gear",test_hardware:"TESTER: Hardware",test_gears:"TESTER: Gears",support_hinge_bolt:"SUPPORT: Hinge Bolt",support_bearing:"SUPPORT: Bearing"]

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

/* [Gear: General] */

// The thickness of the tooth at the "pitch circle".
gear_tooth_thickness=2.5;

gear_tooth_space=1.9;

// Width of the top of the tooth, the "top land".  This is NOT the "face width".
gear_tooth_tip_width=0.5;

// Depth of a tooth.  "Whole" includes clearance space.
gear_tooth_whole_depth=3.3;

gear_tooth_addendum=1.7;

gear_tooth_dedendum=1.6;


/* [Gear: Threaded Rod] */

// Number of teeth.
gear43_tooth_count=43;			

// Height of the gear overall.
gear43_height=7.5;

// Size of the shaft hole.
gear43_shaft_diameter=6.5;

// Size of hex nut hole.
gear43_nut_width=11.5;

// Height of the hex hole recess in the gear.  Consider using 2 nuts for stability, but they must be at least 1/6 turn offset (not touching! they'll bind on the curved rod)
gear43_nut_height=12;

gear43_nut_body_diameter=20;


/* [Gear: Stepper] */

// Number of teeth.
gear10_tooth_count=10;			

// Size of the shaft hole.
gear10_shaft_diameter=5.1;

gear10_shaft_flat_width=3.1;

gear10_shaft_height=6;

gear10_set_screw_diameter=4;


/* [Hidden] */

// might make this not hidden eventually


// the pitch circle circumfrance is based on adding up all the space and tooth thicknesses, use this to calculate diameter
gear43_pitch_d=gear43_tooth_count*(gear_tooth_thickness+gear_tooth_space)/PI;

// outer diameter is then the pitch diameter plus addendum*2
gear43_outer_d=gear43_pitch_d+gear_tooth_addendum*2;

// and inner diameter is pitch diameter minus dedendum*2
gear43_inner_d=gear43_pitch_d-gear_tooth_dedendum*2;


// the pitch circle circumfrance is based on adding up all the space and tooth thicknesses, use this to calculate diameter
gear10_pitch_d=gear10_tooth_count*(gear_tooth_thickness+gear_tooth_space)/PI;

// outer diameter is then the pitch diameter plus addendum*2
gear10_outer_d=gear10_pitch_d+gear_tooth_addendum*2;

// and inner diameter is pitch diameter minus dedendum*2
gear10_inner_d=gear10_pitch_d-gear_tooth_dedendum*2;


// How much length you want to slide the stepper for adjustment.
stepper_adjustment_length=10;

stepper_hole_diameter = 4.5;

// distance between center of the 2 mounting holes
stepper_hole_distance = 35;

stepper_motor_diameter = 28;

stepper_motor_height = 21;

// distance from top of motor to the top of usable thread on the gear
stepper_motor_to_gear_height = 22;

stepper_gear_diameter = 22;

// how far the shaft is offset from the center of the stepper
stepper_motor_to_shaft_radius = 7.25;

hinge_housing_diameter=bearing_diameter+hinge_thickness*2;
tracker_thickness=hinge_housing_diameter/2-2;
tracker_length=bearing_diameter/2+hinge_thickness+tracker_radius;
top_width=hinge_length-bearing_height*2-2;
camera_bolt_housing_diameter=camera_bolt_diameter+hinge_thickness*1.5;
hinge_bolt_housing_diameter=hinge_bolt_diameter+hinge_thickness*2;

tracker_balance_x=tracker_length*0.33;
tracker_balance_T=atan((hinge_length/2-tracker_extra_length)/(tracker_length-tracker_balance_x-tracker_extra_length));


// Gears are set to meet at the "pitch" circle.  Adding a little hard coded slop or imperfections push / shake things in bad ways.
gear_offset_slop=1;
gear_offset=(gear10_pitch_d+gear43_pitch_d)/2+gear_offset_slop;

// Height of the gear overall.
gear10_height=tracker_thickness+gear43_height;

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
            rotate([0,0,tracker_balance_T])
            mirror([0,1,0])
            cube([tracker_length,hinge_length,tracker_thickness*2]);

            // cut other angled bit
            translate([tracker_balance_x+tracker_extra_length,hinge_length,-1])
            rotate([0,0,-tracker_balance_T])
            cube([tracker_length,hinge_length,tracker_thickness*2]);

            // cut motor stuff
            translate([hinge_housing_diameter/2+tracker_radius-gear_offset,hinge_length/2,0])
            rotate([0,0,-90])
            cut_stepper_motor();
        }

        // one part of bearing housing
        part_bearing_housing();

        // other part of bearing housing
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

module support_hinge_bolt()
{
    color("red")
    difference()
    {
        translate([-(hinge_bolt_housing_diameter-hinge_thickness)/2,0,0])
        cube([hinge_bolt_housing_diameter-hinge_thickness,bearing_height,hinge_housing_diameter/2-hinge_bolt_housing_diameter/2+hinge_thickness]);

        translate([0,-1,hinge_housing_diameter/2])
        part_hinge_bolt_housing(h=bearing_height*2);
    }
}

module support_bearing()
{
    color("red")
    translate([hinge_housing_diameter/2,0,0])
    hull()
    {
        translate([0,0,hinge_housing_diameter/2])
        rotate([90,0,0])
        cylinder(d=hinge_housing_diameter-hinge_thickness,h=bearing_height,center=true);
        
        translate([0,0,0.5])
        cube([hinge_housing_diameter-hinge_thickness,bearing_height,1],center=true);
    }
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
            translate([(hinge_housing_diameter-hinge_bolt_housing_diameter)/2,(hinge_length-top_width)/2,hinge_housing_diameter-tracker_thickness])
            cube([tracker_length+tracker_extra_length-hinge_housing_diameter/2+hinge_bolt_housing_diameter/2,top_width,tracker_thickness]);

            // camera mount housing (flush to top so we can flip and print flat)
            translate([tracker_balance_x,(hinge_length-top_width)/2,hinge_housing_diameter-camera_bolt_housing_diameter/2])
            part_camera_bolt_housing();
        }
        
        // cut out the hinge bolt
        translate([hinge_housing_diameter/2,bearing_height,hinge_housing_diameter/2])
        cut_hinge_bolt();
        
        // cut rod hole
        translate([hinge_housing_diameter/2+tracker_radius,hinge_length/2,hinge_housing_diameter/4])
        cut_rod_hole_top();
        
        // cut camera mount rod
        translate([tracker_balance_x,0,hinge_housing_diameter-camera_bolt_housing_diameter/2])
        cut_camera_bolt();
        
        // cut one angled bit
        translate([tracker_balance_x+tracker_extra_length,0,tracker_thickness])
        rotate([0,0,tracker_balance_T])
        mirror([0,1,0])
        cube([tracker_length,top_width,tracker_thickness*2]);

        // cut other angled bit
        translate([tracker_balance_x+tracker_extra_length,hinge_length,tracker_thickness])
        rotate([0,0,-tracker_balance_T])
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

module test_hardware()
{
    test_x=tracker_length*0.23;
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
            translate([hinge_housing_diameter+camera_bolt_housing_diameter/2,0,camera_bolt_diameter/2+hinge_thickness])
            part_camera_bolt_housing(h=test_y);
            
            // hinge bolt test
            translate([hinge_housing_diameter+camera_bolt_housing_diameter+max(rod_diameter,tripod_bolt_diameter)+rod_diameter*1.5+hinge_bolt_housing_diameter/2,0,hinge_bolt_housing_diameter/2])
            part_hinge_bolt_housing(h=test_y);
        }
        
        // cut camera bolt
            translate([hinge_housing_diameter+camera_bolt_housing_diameter/2,0,camera_bolt_diameter/2+hinge_thickness])
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
        translate([hinge_housing_diameter+camera_bolt_housing_diameter+tripod_bolt_diameter/2,bearing_height+(test_y-bearing_height)*3/4,0])
        cut_tripod_hole();

    }
    
    // scope mount..
}

module test_gears()
{
    // create bare outline of rod hole and stepper motor holes
    // use hull and minkowski to create a stepper mount plate
    
    housing_thickness=2;
    hull_height=tracker_thickness;
    
    // rod is at (0,0), figure out where the stepper shaft should be cenetered
    stepper_shaft_xyz=[gear_offset,0,0];

    // 1. hull (minimim shape)
    // 2. minkowski (add material for mounting) [many translations to orient correctly]
    // 3. difference (remove shafts/rods/bolts)

    translate([0,0,-tracker_thickness])
    difference()
    {
        union()
        {
            translate([-rod_diameter/2,0,0]) // translate back to center on rod
            minkowski()
            {
                // translate so the cylinder is centered at (0,0)
                translate([rod_diameter/2,0,0])
                hull()
                {
                    // rod
                    cylinder(d=rod_diameter,h=hull_height/2);
                    
                    // stepper bolts (centered on the motor shaft)
                    translate(stepper_shaft_xyz)
                    rotate([0,0,90])
                    cut_stepper_bolts(h=hull_height/2,z=0);
                }
                cylinder(r=housing_thickness,h=hull_height/2);
            }
        }

        // cut the rod hole
        translate([0,0,tracker_thickness+0.1])
        rotate([0,0,180])
        cut_rod_hole_bottom();

        // cut the stepper bolts and gear
        translate(stepper_shaft_xyz)
        rotate([0,0,90])
        {
            cut_stepper_bolts(h=hull_height*4,z=-1);
            cut_stepper_gear(z=-1);
        }
    }
}

// cenetered with stepper shaft at (0,0)
module cut_stepper_bolts(h=tracker_thickness*2,z=-1)
{
    // bolts
    translate([-stepper_hole_distance/2,-stepper_motor_to_shaft_radius-stepper_adjustment_length/2,z])
    {

        hull()
        {
            cylinder(d=stepper_hole_diameter,h=h);
            
            translate([0,stepper_adjustment_length,0])
            cylinder(d=stepper_hole_diameter,h=h);
        }

        hull()
        {
            translate([stepper_hole_distance,0,0])
            cylinder(d=stepper_hole_diameter,h=h);

            translate([stepper_hole_distance,stepper_adjustment_length,0])
            cylinder(d=stepper_hole_diameter,h=h);
        }
    }
}

// cenetered with stepper shaft at (0,0)
module cut_stepper_gear(z=-1)
{
    // gear
    translate([0,-stepper_adjustment_length/2,z])
    hull() 
    {
        cylinder(d=stepper_gear_diameter,h=stepper_motor_to_gear_height);
        
        translate([0,stepper_adjustment_length,0])
        cylinder(d=stepper_gear_diameter,h=stepper_motor_to_gear_height);
    }
}


module cut_stepper_motor()
{
    cut_stepper_bolts();
    cut_stepper_gear();
}

module pie_slice(id,od,h,degrees=45)
{
    t_x=id<0?0:id/2;
    rotate_extrude(angle=degrees,convexity=2)
    translate([t_x,0,0])
    square([(od-id)/2,h],false);
}


/*
w = width
h = height
s = sides (default 6)
*/
module cut_hex(w,h,s=6) 
{
    // how much rotation per side in degrees, T
    T = 360 / s;
    // figure out the width of one side, x
    x = w * tan(T/2);
    
    // create a cube, translate to be a side, rotate, repeat
    translate([0,0,h/2])
    union()
    {
        for (i = [0:s-1]) {
            rotate([0,0,T*i])
            translate([w/2-x/2,0,0])
            cube([x,x,h],center=true);
        }
    }
}


module part_gear_43() 
{
    // 1. create the teeth
    // 2. fill in the middle
    // 3. cut the shaft
    // 4. cut the nut
    
    // reference: https://en.wikiversity.org/wiki/Gears#/media/File:Gearnomenclature.jpg
    
    t=0.1;
    
    // we have to calculate the gear size from addendum, dedendum, tooth count, space width and tooth thickness
    
    T = 360 / gear43_tooth_count;
    
    // hard coded plate for nut to rest on
    nut_offset_z=2;

    color("cyan")
    difference()
    {
        union()
        {
            // teeth
            translate([0,0,gear43_height/2])
            for (i = [0:gear43_tooth_count-1]) {
                rotate([0,0,T*i])
                hull()
                {
                    // tooth face
                    translate([gear43_outer_d/2-t/2,0,0])
                    cube([t,gear_tooth_tip_width,gear43_height],center=true);
                    
                    // tooth at pitch circle
                    translate([gear43_pitch_d/2-t/2,0,0])
                    cube([t,gear_tooth_thickness,gear43_height],center=true);
                    
                    // tooth at inner (clearance) circle
                    translate([gear43_inner_d/2-t/2,0,0])
                    cube([t,gear_tooth_thickness+gear_tooth_tip_width,gear43_height],center=true);
                }
            }
            
            // main body
            translate([0,0,gear43_height/2])
            cylinder(d=gear43_inner_d+t,h=gear43_height,center=true);

            // nut body
            cylinder(d=gear43_nut_body_diameter,h=nut_offset_z+gear43_nut_height);
        }

        // cut shaft
        cylinder(d=gear43_shaft_diameter,h=gear43_height*2,center=true);

        // cut nut
        translate([0,0,nut_offset_z])
        cut_hex(w=gear43_nut_width,h=gear43_nut_height*2);
    }
}

module part_gear_10()
{
    // close to the 43 tooth gear but..
    // - taller
    // - has set screw
    // - fits on motor shaft (flat sides)
    

    // 1. create the teeth
    // 2. fill in the middle
    // 3. cut the shaft
    // 4. create set screw hole
    
    // reference: https://en.wikiversity.org/wiki/Gears#/media/File:Gearnomenclature.jpg
    
    t=0.1;
    
    // we have to calculate the gear size from addendum, dedendum, tooth count, space width and tooth thickness
    
    
    T = 360 / gear10_tooth_count;
    
    color("cyan")
    difference() 
    {
        translate([0,0,gear10_height/2])
        difference()
        {
            
            union()
            {
                // teeth
                for (i = [0:gear10_tooth_count-1]) {
                    rotate([0,0,T*i])
                    hull()
                    {
                        // tooth face
                        translate([gear10_outer_d/2-t/2,0,0])
                        cube([t,gear_tooth_tip_width,gear10_height],center=true);
                        
                        // tooth at pitch circle
                        translate([gear10_pitch_d/2-t/2,0,0])
                        cube([t,gear_tooth_thickness,gear10_height],center=true);
                        
                        // tooth at inner (clearance) circle
                        translate([gear10_inner_d/2-t/2,0,0])
                        cube([t,gear_tooth_thickness+gear_tooth_tip_width,gear10_height],center=true);
                    }
                }
                
                // main body
                cylinder(d=gear10_inner_d+t,h=gear10_height,center=true);
                
                // flat for the set screw
                color("red",0.1)
                translate([0,0,-gear10_height/2+(gear10_shaft_height*1.5)/2])
                cylinder(d=gear10_outer_d,h=gear10_shaft_height*1.5,center=true);
            }

            // cut shaft (has a flat)
            difference()
            {
                // main body
                cylinder(d=gear10_shaft_diameter,h=gear10_height*2,center=true);
                translate([gear10_shaft_diameter/2+gear10_shaft_flat_width/2,0,0])
                // one flat
                cube([gear10_shaft_diameter,gear10_shaft_diameter,gear10_height*3],center=true);
                // other flat
                translate([-gear10_shaft_diameter/2-gear10_shaft_flat_width/2,0,0])
                cube([gear10_shaft_diameter,gear10_shaft_diameter,gear10_height*3],center=true);
            }
            
            // cut set screw holes
            translate([0,0,-gear10_height/2+(gear10_shaft_height*1.5)/2])
            rotate([0,90,0])
            cylinder(d=gear10_set_screw_diameter,h=gear10_outer_d*2,center=true);
        }
    }
}

if (part == "top") {
    rotate([180,0,0])
    top();
} else if (part == "bottom") {
    bottom();
} else if (part == "bottom_with_gears") {
    bottom();
    
    translate([hinge_housing_diameter/2+tracker_radius,hinge_length/2,tracker_thickness])
    part_gear_43();
    
    translate([hinge_housing_diameter/2+tracker_radius-gear_offset,hinge_length/2,0])
    part_gear_10();
} else if (part == "both") {
    top();
    bottom();
} else if (part == "test_hardware") {
    test_hardware();
} else if (part == "test_gears") {
    test_gears();
} else if (part == "gear43") {
    part_gear_43();
} else if (part == "gear10") {
    part_gear_10();
} else if (part == "support_hinge_bolt") {
    support_hinge_bolt();
} else if (part == "support_bearing") {
    support_bearing();
} 
