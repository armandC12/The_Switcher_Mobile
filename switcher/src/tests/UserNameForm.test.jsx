import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import NameForm from '../components/ui/NameForm';
import { toast } from "@/components/hooks/use-toast";
import "@testing-library/jest-dom";

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

vi.mock("@/context/GameContext", () => ({
  useGameContext: () => ({
    setUsername: vi.fn(), 
  }),
}));

describe("NameForm", () => {
  it("should display validation errors for invalid username", async () => {
    render(
      <MemoryRouter>
        <NameForm />
      </MemoryRouter>
    );

    const usernameInput = screen.getByPlaceholderText("Ingrese su nombre de usuario");
    const submitButton = screen.getByText("Siguiente");

    fireEvent.change(usernameInput, { target: { value: "ab" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText("El nombre de usuario debe tener al menos 3 caracteres.")).toBeInTheDocument();
    });

    fireEvent.change(usernameInput, { target: { value: "averylongusername" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText("El nombre de usuario debe tener como máximo 15 caracteres.")).toBeInTheDocument();
    });
  });

  it("should submit the form and trigger toast for valid username", async () => {
    render(
      <MemoryRouter>
        <NameForm />
      </MemoryRouter>
    );

    const usernameInput = screen.getByPlaceholderText("Ingrese su nombre de usuario");
    const submitButton = screen.getByText("Siguiente");

    fireEvent.change(usernameInput, { target: { value: "validuser" } });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(toast).toHaveBeenCalledWith({
        title: "You submitted the following values:",
        description: expect.anything(),
      });
    });
  });
});
