module tb_module;

reg [3:0] sigin;
wire [3:0] sigout;

initial begin
    $from_myhdl(
        sigin
    );
    $to_myhdl(
        sigout
    );
end

module dut(
    sigin,
    sigout
);

endmodule
