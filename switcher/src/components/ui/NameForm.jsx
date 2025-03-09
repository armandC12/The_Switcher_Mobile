import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { toast } from "@/components/hooks/use-toast"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { useNavigate } from "react-router-dom"
import { useGameContext } from "@/context/GameContext"

const FormSchema = z.object({
  username: z
    .string()
    .min(3, {
      message: "El nombre de usuario debe tener al menos 3 caracteres.",
    })
    .max(15, {
      message: "El nombre de usuario debe tener como máximo 15 caracteres.",
    }),
})

export default function InputForm() {
  const navigate = useNavigate()
  const { setUsername } = useGameContext()

  const form = useForm({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      username: "",
    },
  })

  function onSubmit(data) {
    toast({
      title: "You submitted the following values:",
      description: (
        <pre className="mt-2 w-[340px] rounded-md bg-slate-950 p-4">
          <code className="text-white">{JSON.stringify(data, null, 2)}</code>
        </pre>
      ),
    })

    setUsername(data.username)
    navigate('/games')
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className=" h-60 bg-zinc-900 p-4 rounded-lg shadow-md border border-zinc-800 flex flex-col justify-between">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="block text-lg text-white mb-5">Nombre de usuario</FormLabel>
              <FormControl>
                <Input
                  className="w-full bg-zinc-800  text-white rounded-full px-4 py-5  outline-none border-none !focus:border-none !focus:outline-none"
                  placeholder="Ingrese su nombre de usuario"
                  {...field}
                />
              </FormControl>
              <FormDescription className="text-base mt-5">
                Este nombre será visible para el resto de jugadores.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button className="bg-green-500 text-white py-2 px-6 rounded-lg hover:bg-green-600 transition-all duration-200 w-1/3 self-center" type="submit">
          Siguiente
        </Button>
      </form>
    </Form>
  )
}
