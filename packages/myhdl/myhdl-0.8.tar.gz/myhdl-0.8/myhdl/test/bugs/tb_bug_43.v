module tb_bug_43;

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

bug_43 dut(
    sigin,
    sigout
);

endmodule
