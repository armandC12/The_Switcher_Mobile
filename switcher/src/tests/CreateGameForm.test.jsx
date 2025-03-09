import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { toast } from "@/components/hooks/use-toast"
import "@testing-library/jest-dom"
import CreateGameForm from "@/components/ui/CreateGameForm";

vi.mock('@/context/GameContext', () => ({
  useGameContext: vi.fn(() => ({
    username: 'test123', 
  })),
}));

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

vi.mock("@/components/hooks/use-toast", () => ({
  toast: vi.fn(),
}));

describe("CreateForm", () => {
  it("should display validation errors for invalid name", async () => {
    render(
      <MemoryRouter>
        <CreateGameForm />
      </MemoryRouter>
    );

    const nameInput = screen.getByPlaceholderText("Ingrese el nombre de la partida");
    const submitButton = screen.getByText("Crear");

   
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText("El nombre de la partida es obligatorio")).toBeInTheDocument();
    });

    fireEvent.change(nameInput, { target: { value: "averylongnameforagame" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText("El nombre de la partida debe tener como máximo 15 caracteres.")).toBeInTheDocument();
    });
  });

  it("should submit the form and trigger toast for valid username", async () => {
    render(
      <MemoryRouter>
        <CreateGameForm />
      </MemoryRouter>
    );

    const nameInput = screen.getByPlaceholderText("Ingrese el nombre de la partida");
    const submitButton = screen.getByText("Crear");

    fireEvent.change(nameInput, { target: { value: "validname" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(toast).toHaveBeenCalledWith({
        title: expect.anything(),
        description: expect.anything(),
      });
    });
  });
});
