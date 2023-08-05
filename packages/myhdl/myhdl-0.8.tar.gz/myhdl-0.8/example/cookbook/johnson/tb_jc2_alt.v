module tb_jc2_alt;

reg goLeft;
reg goRight;
reg stop;
reg clk;
wire [3:0] q;

initial begin
    $from_myhdl(
        goLeft,
        goRight,
        stop,
        clk
    );
    $to_myhdl(
        q
    );
end

jc2_alt dut(
    goLeft,
    goRight,
    stop,
    clk,
    q
);

endmodule
