module tb_gray_counter;

reg clk;
reg reset;
reg enable;
wire [7:0] gray_count;

initial begin
    $from_myhdl(
        clk,
        reset,
        enable
    );
    $to_myhdl(
        gray_count
    );
end

gray_counter dut(
    clk,
    reset,
    enable,
    gray_count
);

endmodule
