'''
Module: LFSR
Author: juandisay <juandi.syafrin@gmail.com>
'''

class BasicLFSR:
    """
    A basic Linear Feedback Shift Register (LFSR) implementation 
    with a fixed configuration. This implementation uses a 4-bit 
    register with hardwired feedback function.
    """
    
    def __init__(self, initial_state=0b0110):
        """
        Initialize the LFSR with a given state.
        
        Args:
            initial_state (int): The initial 4-bit state (default: 0110)
        """
        self._state = initial_state & 0b1111  # Ensure 4-bit state
    
    @property
    def state(self):
        """
        Get the current state of the register.
        
        Returns:
            int: The current state as an integer
        """
        return self._state
    
    def next_bit(self):
        """
        Generate the next bit in the stream and update the state.
        
        Returns:
            int: The next bit (0 or 1) in the stream
        """
        # Feedback function: XOR of bits 3 and 2
        feedback = ((self._state >> 3) ^ (self._state >> 2)) & 1
        # Get output bit (rightmost bit)
        output = self._state & 1
        # Shift right and set leftmost bit to feedback
        self._state = ((self._state >> 1) | (feedback << 3)) & 0b1111
        return output


class GeneralLFSR:
    """
    A general-purpose Linear Feedback Shift Register (LFSR) implementation
    that allows customization of register size and tap sequence.
    """
    
    def __init__(self, size, taps, initial_state=None):
        """
        Initialize the LFSR with given parameters.
        
        Args:
            size (int): The size of the register in bits
            taps (list): List of tap positions (0-indexed from right)
            initial_state (int, optional): Initial state. If None, defaults to all 1s
        """
        if size <= 0:
            raise ValueError("Register size must be positive")
        self._size = size
        self._taps = sorted(taps)
        if any(t >= size or t < 0 for t in taps):
            raise ValueError(f"Tap positions must be between 0 and {size-1}")
        
        # Create bit mask for the register size
        self._mask = (1 << size) - 1
        
        # Set initial state
        if initial_state is None:
            initial_state = self._mask
        self._state = initial_state & self._mask
    
    @property
    def size(self):
        """
        Get the size of the register.
        
        Returns:
            int: The size of the register in bits
        """
        return self._size
    
    @property
    def state(self):
        """
        Get the current state of the register.
        
        Returns:
            int: The current state as an integer
        """
        return self._state
    
    @state.setter
    def state(self, value):
        """
        Set the current state of the register.
        
        Args:
            value (int): The new state
        """
        self._state = value & self._mask
    
    def reset(self):
        """
        Reset the register to all 1s."""
        self._state = self._mask
    
    def next_bit(self):
        """
        Generate the next bit in the stream and update the state.
        
        Returns:
            int: The next bit (0 or 1) in the stream
        """
        # Calculate feedback by XORing all tapped bits
        feedback = 0
        for tap in self._taps:
            feedback ^= (self._state >> tap) & 1
        
        # Get output bit (rightmost bit)
        output = self._state & 1
        
        # Shift right and set leftmost bit to feedback
        self._state = ((self._state >> 1) | (feedback << (self._size - 1))) & self._mask
        return output


def test_basic_lfsr():
    """Test the BasicLFSR implementation."""
    print("Testing BasicLFSR:")
    lfsr = BasicLFSR(0b0110)
    
    print("Initial state:", format(lfsr.state, '04b'))
    print("\nGenerating 20 bits:")
    for i in range(20):
        bit = lfsr.next_bit()
        print(f"Step {i+1}: State = {format(lfsr.state, '04b')}, Output = {bit}")


def test_general_lfsr():
    """Test the GeneralLFSR implementation configured to match BasicLFSR."""
    print("\nTesting GeneralLFSR (configured to match BasicLFSR):")
    # Configure with 4-bit register and taps at positions 2 and 3
    lfsr = GeneralLFSR(4, [2, 3], 0b0110)
    
    print("Initial state:", format(lfsr.state, '04b'))
    print("\nGenerating 20 bits:")
    for i in range(20):
        bit = lfsr.next_bit()
        print(f"Step {i+1}: State = {format(lfsr.state, '04b')}, Output = {bit}")


def main():
    """Main function to demonstrate LFSR implementations."""
    test_basic_lfsr()
    test_general_lfsr()

if __name__ == "__main__":
    main()
