module tb_uart_tx_2;

wire tx_bit;
reg tx_valid;
reg [7:0] tx_byte;
reg tx_clk;
reg tx_rst;

initial begin
    $from_myhdl(
        tx_valid,
        tx_byte,
        tx_clk,
        tx_rst
    );
    $to_myhdl(
        tx_bit
    );
end

uart_tx_2 dut(
    tx_bit,
    tx_valid,
    tx_byte,
    tx_clk,
    tx_rst
);

endmodule
