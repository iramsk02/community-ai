import { FieldValues, Path, UseFormRegister } from "react-hook-form";

export type InputType = "text" | "email" | "password";

export type FormFieldProps<T extends FieldValues> = {
    id: Path<T>;
    label: string;
    type: InputType;
    placeholder?: string;
    icon?: React.ReactNode;
    register?: UseFormRegister<T>;
    error?: string;
};