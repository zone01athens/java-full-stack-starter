package athens.piscine;

public class Greeting {
    public static String forName(String name) {
        return "Hello, " + name + "!";
    }

    public static void main(String[] args) {
        System.out.println(forName(args.length == 0 ? "Athens" : args[0]));
    }
}
