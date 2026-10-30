pub fn shipping(weight: u32, zone: u8, express: bool, insured: bool, member: bool) -> u32 {
    let mut cost = 0;
    if weight > 20 {
        cost += 40;
    } else if weight > 10 {
        cost += 25;
    } else if weight > 5 {
        cost += 15;
    } else {
        cost += 8;
    }
    if zone == 1 {
        cost += 2;
    } else if zone == 2 {
        cost += 6;
    } else if zone == 3 {
        cost += 11;
    }
    if express {
        cost *= 2;
    }
    if insured {
        cost += 5;
    }
    if member && cost > 20 {
        cost -= 4;
    }
    if member && express {
        cost -= 2;
    }
    if cost > 100 {
        cost = 100;
    }
    cost
}
