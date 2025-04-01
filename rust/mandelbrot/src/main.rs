use num::complex::Complex64;


// https://en.wikipedia.org/wiki/Mandelbrot_set#Computer_drawings
//
struct LinearMap {
    a0: f64,
    a1: f64,
    b0: f64,
    b1: f64,
}

fn linear_map_to_a(map: &LinearMap, b:f64) -> f64 {
    let r = (b - map.b0) / (map.b1 - map.b0);
    return (map.a1 - map.a0)*r + map.a0;
}

fn intterate_z(c: Complex64, upper_bound: f64, max_itterations: u32) -> i32 {
    let mut i : i32 = 0;
    let mut z = Complex64{ re:0.0, im:0.0 };
    while z.re.abs() < upper_bound && z.im.abs() < upper_bound {
        if i as u32 > max_itterations {
            return -1;
        }
        z = z*z + c;
        i+=1;
    }
    return i
}

fn compute_diagram(map_real: &LinearMap, map_imag: &LinearMap) -> Vec<Vec<i32>> {
    let buffer_x = (map_real.b1) as usize;
    let buffer_y = (map_imag.b1) as usize;
    let mut buffer = vec![vec![0; buffer_x]; buffer_y];
    for y in 0..buffer.len() {
        for x in 0..buffer[y].len() {
            let a = linear_map_to_a(map_real, x as f64);
            let b = linear_map_to_a(map_imag, y as f64);
            let c = Complex64 { re: a, im: b };
            buffer[y][x] = intterate_z(c, 10000.0, 100);
        }
    }
    return buffer
}

fn main() {
    let lin_real = LinearMap {
        a0: -2.0,
        a1: 2.0,
        b0: 0.0,
        b1: 80.0,
    };
    let lin_imag = LinearMap {
        a0: -2.0,
        a1: 2.0,
        b0: 0.0,
        b1: 40.0,
    };

    let buffer = compute_diagram(&lin_real, &lin_imag);

    let by_intensity = "`.-':_,^=;><+rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@";
    // Iterate over buffer, outputting each value to stdout
    // and using the value to index into a string of characters
    for y in 0..buffer.len() {
        for x in 0..buffer[y].len() {
            let i = buffer[y][x];
            if i < 0 {
                print!(" ")
            } else if i >= (by_intensity.len() as i32) {
                print!("!");
            }
            else {
                let c = by_intensity.chars().nth(i as usize).unwrap();
                print!("{}", c);
            }

        }
        println!();
    }






}
