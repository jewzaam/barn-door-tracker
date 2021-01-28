

box_thickness=2;

box_hole_width=5;

box_hole_depth=10;

box_inner_dim=[33,36,25];

/* [Hidden] */

$fn = 300;


module lid()
{
    // lid
    union()
    {
        cube([box_inner_dim[0]+box_thickness*2,box_inner_dim[1]+box_thickness*2,box_thickness]);

        translate([box_thickness,box_thickness,0])
        cube([box_inner_dim[0],box_inner_dim[1],box_thickness*2]);
    }
}

// box
module box()
{
    difference()
    {
        // main body
        cube(box_inner_dim+[box_thickness*2,box_thickness*2,box_thickness*2]);

        // cut inside
        translate([box_thickness,box_thickness,box_thickness])
        cube(box_inner_dim+[0,0,box_thickness*2]);
        
        // cut slot for wires
        translate([box_thickness+box_inner_dim[0]/2-box_hole_width/2,-box_thickness,box_thickness*2+box_inner_dim[2]-box_hole_depth])
        cube([box_hole_width,box_inner_dim[1]+box_thickness*4,box_hole_depth+box_thickness]);
    }
    
}

lid();