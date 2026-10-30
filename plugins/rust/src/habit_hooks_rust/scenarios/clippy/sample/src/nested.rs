pub struct Ladder;

impl Ladder {
    pub fn classify(x: i32) -> i32 {
        if x > 0 {
            if x > 1 {
                if x > 2 {
                    if x > 3 {
                        if x > 4 {
                            return 5;
                        }
                    }
                }
            }
        }
        0
    }
}
