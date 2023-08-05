module tb_pcie_legacyint_next_state_logic;

reg [1:0] state_i;
wire [1:0] next_state_o;
wire next_state_en_o;
reg interrupt_pending_i;
wire interrupt_assert_o;

initial begin
    $from_myhdl(
        state_i,
        interrupt_pending_i
    );
    $to_myhdl(
        next_state_o,
        next_state_en_o,
        interrupt_assert_o
    );
end

pcie_legacyint_next_state_logic dut(
    state_i,
    next_state_o,
    next_state_en_o,
    interrupt_pending_i,
    interrupt_assert_o
);

endmodule
