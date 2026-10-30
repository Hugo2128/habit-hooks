pub fn bill(net: u32, tax: u32, discount: u32, shipping: u32, tip: u32, fee: u32) -> u32 {
    net + tax - discount + shipping + tip + fee
}
