
/* [Teeth] */
// Number of teeth.
tooth_count=43;			

// The thickness of the tooth at the "pitch circle".
tooth_thickness=2.5;

tooth_space=1.9;

// Width of the top of the tooth, the "top land".  This is NOT the "face width".
tooth_tip_width=0.5;

// Depth of a tooth.  "Whole" includes clearance space.
tooth_whole_depth=3.3;

tooth_addendum=1.7;

tooth_dedendum=1.6;

/* [Gear] */
// Height of the gear overall.
gear_height=7.5;

// Size of the shaft hole.
shaft_diameter=6.5;

// Number of extra material "slices" to remove.
remove_count=0;

// How wide each removed slice is in degrees.
remove_degrees=50;

// Inner diameter of removed slice.
remove_inner_diameter=20;

// Outer diameter of removed slice.
remove_outer_diameter=50;

/* [Nut] */
// Size of hex hole.  Set to 0 if no hex (i.e. for a nut).
nut_width=11;

// Height of the hex hole recess in the gear.  Ignored if nut_width = 0.
nut_height=5.5;

/* [Cleanup

/* [Other] */
//Resolution of the donut.
res = 200;		//[1:300]

/* [Hidden] */

$fn = res;

module pie_slice(id,od,h,degrees=45)
{
    t_x=id<0?0:id/2;
    rotate_extrude(angle=degrees,convexity=2)
    translate([t_x,0,0])
    square([(od-id)/2,h],false);
}


module gear() {
    // 1. create the teeth
    // 2. fill in the middle
    // 3. cut the shaft
    // 4. cut "pie" slices
    
    // reference: https://en.wikiversity.org/wiki/Gears#/media/File:Gearnomenclature.jpg
    
    t=0.1;
    
    // we have to calculate the gear size from addendum, dedendum, tooth count, space width and tooth thickness
    
    // the pitch circle circumfrance is based on adding up all the space and tooth thicknesses, use this to calculate diameter
    pitch_d=tooth_count*(tooth_thickness+tooth_space)/PI;

    // outer diameter is then the pitch diameter plus addendum*2
    outer_d=pitch_d+tooth_addendum*2;
    
    // and inner diameter is pitch diameter minus dedendum*2
    inner_d=pitch_d-tooth_dedendum*2;
    
    T = 360 / tooth_count;
    
    color("cyan")
    translate([0,0,gear_height/2])
    difference()
    {
        union()
        {
            // teeth
            for (i = [0:tooth_count-1]) {
                rotate([0,0,T*i])
                hull()
                {
                    // tooth face
                    translate([outer_d/2-t/2,0,0])
                    cube([t,tooth_tip_width,gear_height],center=true);
                    
                    // tooth at pitch circle
                    translate([pitch_d/2-t/2,0,0])
                    cube([t,tooth_thickness,gear_height],center=true);
                    
                    // tooth at inner (clearance) circle
                    translate([inner_d/2-t/2,0,0])
                    cube([t,tooth_thickness+tooth_tip_width,gear_height],center=true);
                }
            }
            
            // main body
            cylinder(d=inner_d+t,h=gear_height,center=true);
        }

        // shaft
        cylinder(d=shaft_diameter,h=gear_height*2,center=true);

        // material removal
        if (remove_count > 0) {
            translate([0,0,-gear_height])
            for (p = [0:remove_count-1]) {
                rotate([0,0,360 / remove_count * p])
                pie_slice(od=remove_outer_diameter,id=remove_inner_diameter,h=gear_height*2,degrees=remove_degrees);
            }
        }
    }
    
}

/*
w = width
h = height
s = sides (default 6)
*/
module nut(w,h,s=6) 
{
    // how much rotation per side in degrees, T
    T = 360 / s;
    // figure out the width of one side, x
    x = w * tan(T/2);
    
    // create a cube, translate to be a side, rotate, repeat
    translate([0,0,h])
    union()
    {
        for (i = [0:s-1]) {
            rotate([0,0,T*i])
            translate([w/2-x/2,0,0])
            cube([x,x,h],center=true);
        }
    }
}

difference()
{
    //translate([0,0,height/2])
    gear(); 

    if (nut_width > 0) {
        // the nut is centered, translate so we can cut it out of the cog at the TOP
        translate([0,0,gear_height/2-nut_height/2])
        nut(w=nut_width,h=nut_height);
    }
}