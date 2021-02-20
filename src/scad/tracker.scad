part = "test_hardware"; // [test_hardware:"TEST: Hardware",gear_rod:"GEAR: Rod",gear_stepper:"GEAR: Stepper",test_gears:"TEST: Gears",support_bearing:"SUPPORT: Bearing",top:"TRACKER: Top",bottom:"TRACKER: Bottom",compass:"HELPER: Compass",debug_bottom:"DEBUG: Bottom",debug_tracker:"DEBUG: Tracker"]


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

// angel to cut out for the curve in the rod (bottom plate only)
rod_T=35;

/* [Gear: General] */

// The thickness of the tooth at the "pitch circle".
gear_tooth_thickness=2.5;

gear_tooth_space=1.9;

// Width of the part_top of the tooth, the "part_top land".  This is NOT the "face width".
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

// Size of hex nut hole.
gear43_nut_width=11.5;

// Height of the hex hole recess in the gear.  Consider using 2 nuts for stability, but they must be at least 1/6 turn offset (not touching! they'll bind on the curved rod)
gear43_nut_height=6;

gear43_nut_body_diameter=20;


/* [Gear: Stepper] */

// Number of teeth.
gear10_tooth_count=10;			

// Size of the shaft hole.
gear10_shaft_diameter=5.1;

gear10_shaft_flat_width=3.1;

gear10_shaft_height=6;

gear10_set_screw_diameter=3.7;


/* [Compass] */

// actual diameter of the rod.. rod_diameter is used for holes, this is used for the compass
rod_diameter_actual = 6.35;

compass_hole_diameter=1.8;

compass_height=2;

compass_width=4;

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

// distance from part_top of motor to the part_top of usable thread on the gear
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


// Gears are set to meet at the "pitch" circle ideally.  We allow for adjustment so this is just to center for those adjustments.
gear_offset=(gear10_pitch_d+gear43_pitch_d)/2;

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
            
            rotate([0,rod_T,0])
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
        
        // cut out room for the tracker part_top
        translate([-1,bearing_height,-1])
        cube([tracker_length,hinge_length-bearing_height*2,tracker_thickness+hinge_housing_diameter]);

        // cut out the bearing
        translate([hinge_housing_diameter/2,-1,hinge_housing_diameter/2])
        rotate([-90,0,0])
        cylinder(d=bearing_diameter,h=hinge_length*1.1);
    }
}

module part_bottom()
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

module subpart_hinge_bolt_housing(h)
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

module part_support_bearing()
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

module subpart_finder(l=top_width,trans=true)
{
    offset_x=(hinge_housing_diameter-hinge_bolt_housing_diameter)/2;
    od=10;
    id=7;
    w=14.2;
    recess_w=10.6;
    recess_h=2.5;
    
    translate([trans?-offset_x:0,trans?(hinge_length-l)/2:0,trans?hinge_housing_diameter-w:0])
    difference()
    {
        cube([offset_x+od,l,w]);

        translate([od/2,-1,tracker_thickness/2])
        rotate([-90,0,0])
        cylinder(d=id,h=l*2);

        translate([recess_h,0,recess_h])
        rotate([0,-135,0])
        translate([-recess_w/2,1,recess_w/2])
        cube([recess_w,l*2,recess_w],center=true);

        translate([recess_h,0,w-recess_h])
        rotate([0,45,0])
        translate([-recess_w/2,1,recess_w/2])
        cube([recess_w,l*2,recess_w],center=true);
    }
}

module part_top()
{
    difference()
    {
        union()
        {
            // bolt housing
            translate([hinge_housing_diameter/2,bearing_height,hinge_housing_diameter/2])
            subpart_hinge_bolt_housing(h=hinge_length-bearing_height*2);
            
            // main body
            translate([(hinge_housing_diameter-hinge_bolt_housing_diameter)/2,(hinge_length-top_width)/2,hinge_housing_diameter-tracker_thickness])
            cube([tracker_length+tracker_extra_length-hinge_housing_diameter/2+hinge_bolt_housing_diameter/2,top_width,tracker_thickness]);

            // camera mount housing (flush to part_top so we can flip and print flat)
            translate([tracker_balance_x,(hinge_length-top_width)/2,hinge_housing_diameter-camera_bolt_housing_diameter/2])
            subpart_camera_bolt_housing();

            // quick finder, it has a flat surface, a tube (naked eye), and can attach an ez-finder red dot
            subpart_finder();
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

module subpart_camera_bolt_housing(h=top_width)
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

module part_test_hardware()
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
            subpart_camera_bolt_housing(h=test_y);
            
            // hinge bolt test
            translate([hinge_housing_diameter+camera_bolt_housing_diameter+max(rod_diameter,tripod_bolt_diameter)+rod_diameter*1.5+hinge_bolt_housing_diameter/2,0,hinge_bolt_housing_diameter/2])
            subpart_hinge_bolt_housing(h=test_y);

            // basic scope thinggie, set trans so it's on 0,0,0 and we can move it
            // note this finder setup hard codes some things, I didn't genearlize so having to hard code here too.. ugly!
            finder_y=10;
            translate([(hinge_housing_diameter-hinge_bolt_housing_diameter)/2+10,test_y-finder_y,0])
            subpart_finder(l=finder_y,trans=false);
        }
        
        // cut camera bolt
        translate([hinge_housing_diameter+camera_bolt_housing_diameter/2,0,camera_bolt_diameter/2+hinge_thickness])
        cut_camera_bolt();
                
        // rod test, part_top
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

module part_test_gears()
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


module part_gear_rod() 
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
        cylinder(d=rod_diameter,h=gear43_height*2,center=true);

        // cut nut
        translate([0,0,nut_offset_z])
        cut_hex(w=gear43_nut_width,h=gear43_nut_height*2);
    }
}

module part_gear_stepper()
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

module part_compass()
{
    compass_r=tracker_radius-rod_diameter_actual/2;

    difference()
    {
        hull()
        {
            cylinder(d=compass_width,h=compass_height,center=true);

            translate([compass_r,0,0])
            cylinder(d=compass_width,h=compass_height,center=true);
        }

        cylinder(d=compass_hole_diameter,h=compass_height*2,center=true);

        translate([compass_r,0,0])
        cylinder(d=compass_hole_diameter,h=compass_height*2,center=true);
    }
}

if (part == "test_hardware") {
    part_test_hardware();
} else if (part == "gear_rod") {
    part_gear_rod();
} else if (part == "gear_stepper") {
    part_gear_stepper();
} else if (part == "test_gears") {
    part_test_gears();
} else if (part == "support_bearing") {
    part_support_bearing();
} else if (part == "top") {
    rotate([180,0,0])
    part_top();
} else if (part == "bottom") {
    part_bottom();
} else if (part == "compass") {
    part_compass();
} else if (part == "debug_bottom") {
    part_bottom();
    
    translate([hinge_housing_diameter/2+tracker_radius,hinge_length/2,tracker_thickness])
    part_gear_rod();
    
    translate([hinge_housing_diameter/2+tracker_radius-gear_offset,hinge_length/2,0])
    part_gear_stepper();
} else if (part == "debug_tracker") {
    part_top();
    part_bottom();
}