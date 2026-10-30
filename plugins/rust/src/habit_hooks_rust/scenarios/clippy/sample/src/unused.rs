use std::collections::HashMap;

fn never_called() {}

pub fn count(items: &[u32]) -> usize {
    let total: u32 = items.iter().sum();
    items.len()
}
