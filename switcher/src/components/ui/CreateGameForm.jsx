import { z } from "zod";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import React, { useState } from "react";
import Slider from '@mui/material/Slider';
import { Button } from "./button";
import { useGameContext } from "@/context/GameContext";
import { useNavigate } from "react-router-dom";
import { toast } from "../hooks/use-toast";
import { submitForm } from "@/services/services";


const MAX_PLAYERS = 4;
const MIN_PLAYERS = 2;

const formSchema = z.object({
  name: z.string().min(1, "El nombre de la partida es obligatorio")
    .max(15, {
      message: "El nombre de la partida debe tener como máximo 15 caracteres.",
    }),
  password: z.string()
    .optional()
    .refine(val => val === undefined || val === '' || (val.length >= 8 && val.length <= 16), {
      message: "La contraseña debe tener entre 8 y 16 caracteres.",
    }),
  playersRange: z.array(z.number()).length(2).refine(([min, max]) => min >= MIN_PLAYERS && max <= MAX_PLAYERS, {
    message: `El rango de jugadores debe estar entre ${MIN_PLAYERS} y ${MAX_PLAYERS}.`,
  })
});

function FormSlider({ value, onChange }) {
  return (
    <Slider
      data-testid="players-slider"
      value={value}
      onChange={(event, newValue) => onChange(newValue)}
      valueLabelDisplay='auto'
      min={MIN_PLAYERS}
      max={MAX_PLAYERS}
      sx={{
        width: 250,
        color: '#22c55e',
        '& .MuiSlider-thumb': {
          backgroundColor: '#22c55e',
        },
        '& .MuiSlider-track': {
          backgroundColor: '#22c55e',
        },
        '& .MuiSlider-rail': {
          backgroundColor: '#22c55e',
        },
      }}
    />
  );
}

export default function CreateGameForm() {
  const [errorMessage, setErrorMessage] = useState('');
  const { username, setPlayerId } = useGameContext();
  const navigate = useNavigate();

  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: '',
      password: '',
      playersRange: [MIN_PLAYERS, MAX_PLAYERS],
    },
  });

  const onSubmit = async (data) => {
    console.log(data)
    toast({
      title: "You submitted the following values:",
      description: (
        <pre className="mt-2 w-[340px] rounded-md bg-slate-950 p-4">
          <code className="text-white">{JSON.stringify(data, null, 2)}</code>
        </pre>
      ),
    });

    try {
      const result = await submitForm(data, username);
      setPlayerId(result.player.id);
      navigate(`/games/lobby/${result.game.id}/${result.player.id}`);
    }
    catch (error) {
      setErrorMessage(error.message);

    }
  };

  return (
    <form
      data-testid="formComponent"
      onSubmit={form.handleSubmit(onSubmit)}
      className=" bg-zinc-900 p-8 rounded-lg shadow-md border border-zinc-800 max-w-lg mx-auto"
    >

      <div className="mb-6">
        <label className="block text-lg text-white mb-2">Nombre de la partida</label>
        <input
          placeholder="Ingrese el nombre de la partida"
          {...form.register('name')}
          className="w-full bg-zinc-800 text-white rounded-full px-4 py-2 focus:outline-none"
        />
        {form.formState.errors.name && <p className="text-red-500 mt-1">{form.formState.errors.name.message}</p>}
      </div>

      <div className="mb-6">
        <label className="block text-lg text-white mb-2">Rango de jugadores</label>
        <div className="flex justify-center">
          <Controller
            name="playersRange"
            control={form.control}
            render={({ field }) => (
              <FormSlider value={field.value} onChange={field.onChange} />
            )}
          />
        </div>
        {form.formState.errors.playersRange && <p className="text-red-500 text-center mt-1">{form.formState.errors.playersRange.message}</p>}
      </div>

       {/* Password Field */}
       <div className="mb-6">
        <label className="block text-lg text-white mb-2">Contraseña (opcional)</label>
        <input
          type="password"
          placeholder="Ingrese una contraseña"
          {...form.register('password')}
          className="w-full bg-zinc-800 text-white  rounded-full px-4 py-2 focus:outline-none"
        />
        {form.formState.errors.password && <p className="text-red-500 mt-1">{form.formState.errors.password.message}</p>}
      </div>


      {/* Centered button */}
      <div className="flex justify-center">
        <Button type="submit" className="bg-green-500 text-white py-2 px-6 rounded-lg hover:bg-green-600 transition-all duration-200 w-1/3">
          Crear
        </Button>
      </div>

      {errorMessage && <p className="text-red-500 mt-4 text-center">{errorMessage}</p>}
    </form>
  );
}
