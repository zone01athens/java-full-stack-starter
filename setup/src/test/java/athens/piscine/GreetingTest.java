package athens.piscine;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

class GreetingTest {
    @Test
    void greetsTheGivenPerson() {
        assertEquals("Hello, Ada!", Greeting.forName("Ada"));
    }
}
