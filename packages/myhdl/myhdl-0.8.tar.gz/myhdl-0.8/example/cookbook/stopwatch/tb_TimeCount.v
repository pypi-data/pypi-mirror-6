module tb_TimeCount;

wire [3:0] tens;
wire [3:0] ones;
wire [3:0] tenths;
reg startstop;
reg reset;
reg clock;

initial begin
    $from_myhdl(
        startstop,
        reset,
        clock
    );
    $to_myhdl(
        tens,
        ones,
        tenths
    );
end

TimeCount dut(
    tens,
    ones,
    tenths,
    startstop,
    reset,
    clock
);

endmodule
