module tb_SineComputer;

wire [19:0] cos_z0;
wire [19:0] sin_z0;
wire done;
reg [19:0] z0;
reg start;
reg clock;
reg reset;

initial begin
    $from_myhdl(
        z0,
        start,
        clock,
        reset
    );
    $to_myhdl(
        cos_z0,
        sin_z0,
        done
    );
end

SineComputer dut(
    cos_z0,
    sin_z0,
    done,
    z0,
    start,
    clock,
    reset
);

endmodule
