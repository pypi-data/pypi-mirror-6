module tb_bug_3577799;

reg clk;
reg reset_clk;
reg [15:0] wr_data;
reg wr;
wire [15:0] rd_data;

initial begin
    $from_myhdl(
        clk,
        reset_clk,
        wr_data,
        wr
    );
    $to_myhdl(
        rd_data
    );
end

bug_3577799 dut(
    clk,
    reset_clk,
    wr_data,
    wr,
    rd_data
);

endmodule
