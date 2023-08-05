module tb_latch;

wire q;
reg d;
reg g;

initial begin
    $from_myhdl(
        d,
        g
    );
    $to_myhdl(
        q
    );
end

latch dut(
    q,
    d,
    g
);

endmodule
