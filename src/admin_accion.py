from cruds.usuario_crud import UsuarioCRUD
from cruds.empleado_crud import EmpleadoCRUD
from cruds.tipo_documento_crud import TipoDocumentoCRUD
from cruds.sede_crud import SedeCRUD
from cruds.rol_crud import RolCRUD
from auth.security import Security
import getpass
from sqlalchemy.orm import Session
from entities.empleado import EmpleadoCreate
from entities.usuario import UsuarioCreate
from entities.rol import Rol
from datetime import datetime
import re


class AdminAcciones:
    def __init__(self, db: Session):
        self.db = db
        self.usuario_crud = UsuarioCRUD(db=db)
        self.empleado_crud = EmpleadoCRUD(db=db)
        self.tipo_documento_crud = TipoDocumentoCRUD(db=db)
        self.sede_crud = SedeCRUD(db=db)
        self.rol_crud = RolCRUD()
        self.usuario_actual = None

    def _menu_generico(self, titulo, opciones):
        while True:
            print(f"\n{'='*50}")
            print(f"GESTIÓN DE {titulo.upper()}".center(50))
            print("=" * 50)
            for i, opcion in enumerate(opciones, 1):
                print(f"{i}. {opcion}")
            print("0. Volver al menú anterior")

            opcion = int(input("\nSeleccione una opción: ").strip())
            if 1 <= opcion <= len(opciones):
                return opcion
            elif opcion == 0:
                return None
            else:
                print("Opción no válida. Intente de nuevo.")

    def obtener_id_rol_por_nombre(self, nombre: str):
        """Obtiene el UUID del rol por su nombre usando RolCRUD (case-insensitive)."""
        if not nombre:
            return None
        try:
            rol = self.rol_crud.obtener_por_nombre(self.db, nombre.strip())
            return rol.id_rol if rol else None
        except Exception:
            return None

    def gestionar_empleados(self):
        while True:
            opcion = self._menu_generico(
                "Empleados",
                [
                    "Crear empleado",
                    "Listar empleados",
                    "Editar empleado",
                    "Eliminar empleado",
                ],
            )

            if opcion is None:
                break

            if opcion == 1:
                # Crear empleado
                while True:
                    print("\n" + "-" * 50)
                    print("CREAR EMPLEADO".center(50))
                    print("-" * 50)

                    try:
                        # 1) Datos de acceso (Usuario)
                        while True:
                            nombre_usuario = input("Nombre de usuario: ").strip()
                            if not nombre_usuario:
                                print("El nombre de usuario es requerido.")
                                continue
                            if not re.match(r"^[a-zA-Z0-9._]{4,50}$", nombre_usuario):
                                print(
                                    "El nombre de usuario debe tener 4-50 caracteres y solo letras, números, puntos o guiones bajos."
                                )
                                continue
                            if self.usuario_crud.obtener_por_nombre_usuario(
                                nombre_usuario
                            ):
                                print(
                                    "Ya existe un usuario con ese nombre. Intente otro."
                                )
                                continue
                            break

                        while True:
                            contrasena = getpass.getpass("Contraseña: ")
                            confirmar = getpass.getpass("Confirmar contraseña: ")
                            if contrasena != confirmar:
                                print("Las contraseñas no coinciden. Intente de nuevo.")
                                continue
                            valida, msg = Security.validar_contrasena(contrasena)
                            if not valida:
                                print(f"Contraseña inválida: {msg}")
                                continue
                            break

                        # 2) Datos personales y laborales
                        # Nombres y apellidos
                        def _input_nombre(etiqueta, requerido=True):
                            while True:
                                valor = input(f"{etiqueta}: ").strip()
                                if not valor and not requerido:
                                    return None
                                if not valor:
                                    print("Este campo es requerido.")
                                    continue
                                if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", valor):
                                    print("Solo se permiten letras y espacios.")
                                    continue
                                if len(valor) > 50:
                                    print("Máximo 50 caracteres.")
                                    continue
                                return valor.title()

                        primer_nombre = _input_nombre("Primer nombre")
                        segundo_nombre = _input_nombre(
                            "Segundo nombre (opcional)", requerido=False
                        )
                        primer_apellido = _input_nombre("Primer apellido")
                        segundo_apellido = _input_nombre(
                            "Segundo apellido (opcional)", requerido=False
                        )

                        # Tipos de documento (desde CRUD)
                        tipos_doc = self.tipo_documento_crud.get_activos(
                            db=self.db, skip=0, limit=100
                        )
                        if not tipos_doc:
                            print(
                                "No hay tipos de documento activos configurados. Configure uno antes de continuar."
                            )
                            break

                        print("\nTipos de documento disponibles:")
                        for i, t in enumerate(tipos_doc, 1):
                            # Mostrar nombre y código si existen
                            codigo = getattr(t, "codigo", "") or ""
                            print(f"{i}. {t.nombre} {f'({codigo})' if codigo else ''}")
                        while True:
                            try:
                                idx = int(
                                    input(
                                        "Seleccione el número del tipo de documento: "
                                    ).strip()
                                )
                                if 1 <= idx <= len(tipos_doc):
                                    tipo_doc_sel = tipos_doc[idx - 1]
                                    break
                            except ValueError:
                                pass
                            print("Opción no válida. Intente de nuevo.")

                        # Número de documento (validación básica del CRUD)
                        while True:
                            documento = input("Número de documento: ").strip()
                            if not documento:
                                print("El número de documento es requerido.")
                                continue
                            # Verificar duplicado de documento con CRUD
                            try:
                                if self.empleado_crud.obtener_por_documento(
                                    self.db, documento
                                ):
                                    print("Ya existe un empleado con ese documento.")
                                    continue
                            except Exception:
                                pass
                            break

                        # Fecha de nacimiento y validación de edad
                        fecha_nacimiento = self._validar_entrada(
                            "Fecha de nacimiento (YYYY-MM-DD): ", tipo="fecha"
                        )
                        hoy = datetime.now().date()
                        edad = (
                            hoy.year
                            - fecha_nacimiento.year
                            - (
                                (hoy.month, hoy.day)
                                < (fecha_nacimiento.month, fecha_nacimiento.day)
                            )
                        )
                        if edad < 18 or edad > 80:
                            print("La edad debe estar entre 18 y 80 años.")
                            continue

                        telefono = self._validar_entrada("Teléfono: ", tipo="telefono")

                        # Correo único
                        while True:
                            correo = self._validar_entrada(
                                "Correo electrónico: ", tipo="email"
                            )
                            try:
                                if self.empleado_crud.obtener_por_email(self.db, correo):
                                    print("Ya existe un empleado con ese correo.")
                                    continue
                            except Exception:
                                pass
                            break

                        direccion = self._validar_entrada(
                            "Dirección: ", tipo="texto", min_length=5, max_length=200
                        )

                        tipos_empleado_validos = self.empleado_crud.cargos_permitidos
                        print("\nTipos de empleado:")
                        for i, te in enumerate(tipos_empleado_validos, 1):
                            print(f"{i}. {te}")
                        while True:
                            try:
                                idx_te = int(
                                    input(
                                        "Seleccione el número del tipo de empleado: "
                                    ).strip()
                                )
                                if 1 <= idx_te <= len(tipos_empleado_validos):
                                    tipo_empleado = tipos_empleado_validos[idx_te - 1]
                                    break
                            except ValueError:
                                pass
                            print("Opción no válida. Intente de nuevo.")

                        salario = float(
                            self._validar_entrada("Salario: ", tipo="numero")
                        )
                        if salario > 50000000:
                            print("El salario no puede exceder 50,000,000.")
                            continue

                        fecha_ingreso = self._validar_entrada(
                            "Fecha de ingreso (YYYY-MM-DD): ", tipo="fecha"
                        )
                        if fecha_ingreso > hoy:
                            print("La fecha de ingreso no puede ser futura.")
                            continue
                        if (hoy - fecha_ingreso).days > 18250:
                            print(
                                "La fecha de ingreso no puede ser mayor a 50 años atrás."
                            )
                            continue

                        # Sedes (desde CRUD)
                        sedes = self.sede_crud.get_activas(db=self.db, skip=0, limit=100)
                        if not sedes:
                            print(
                                "No hay sedes activas configuradas. Configure una antes de continuar."
                            )
                            break
                        print("\nSedes disponibles:")
                        for i, s in enumerate(sedes, 1):
                            print(f"{i}. {s.ciudad} - {s.direccion}")
                        while True:
                            try:
                                idx_s = int(
                                    input("Seleccione el número de la sede: ").strip()
                                )
                                if 1 <= idx_s <= len(sedes):
                                    sede_sel = sedes[idx_s - 1]
                                    break
                            except ValueError:
                                pass
                            print("Opción no válida. Intente de nuevo.")

                        # Confirmación
                        print("\nResumen de creación:")
                        print(f"Usuario: {nombre_usuario}")
                        print(
                            f"Empleado: {primer_nombre} {segundo_nombre or ''} {primer_apellido} {segundo_apellido or ''}"
                        )
                        print("Documento: (seleccionado) - oculto por validación básica")
                        print(f"Correo: {correo}")
                        print(f"Teléfono: {telefono}")
                        print(f"Dirección: {direccion}")
                        print(f"Tipo de empleado: {tipo_empleado}")
                        print(f"Salario: {salario}")
                        print(f"Fecha de ingreso: {fecha_ingreso}")
                        print(f"Sede: {sede_sel.ciudad} - {sede_sel.direccion}")

                        confirmar = (
                            input("\n¿Confirmar creación? (s/n): ").strip().lower()
                        )
                        if confirmar != "s":
                            cancelar = (
                                input("¿Cancelar la creación? (s/n): ").strip().lower()
                            )
                            if cancelar == "s":
                                print("Operación cancelada.")
                                break
                            else:
                                continue

                        # Crear usuario y empleado (vía CRUDs)
                        try:
                            id_rol_empleado = self.obtener_id_rol_por_nombre("empleado")
                            if not id_rol_empleado:
                                print(
                                    "No se encontró el rol 'empleado'. Debe crearlo previamente para continuar."
                                )
                                break

                            usuario_nuevo = UsuarioCreate(
                                primer_nombre=primer_nombre,
                                segundo_nombre=segundo_nombre,
                                primer_apellido=primer_apellido,
                                segundo_apellido=segundo_apellido,
                                nombre_usuario=nombre_usuario,
                                password=contrasena,
                                rol=id_rol_empleado,
                            )
                            usuario_creado = self.usuario_crud.crear(
                                datos_entrada=usuario_nuevo
                            )
                            if not usuario_creado:
                                print(
                                    "\nError al crear el usuario. No se creó el empleado."
                                )
                                continue

                            if not self.usuario_actual or not getattr(
                                self.usuario_actual, "id_usuario", None
                            ):
                                print(
                                    "Error: No hay usuario actual autenticado para auditoría."
                                )
                                # Limpiar usuario creado
                                try:
                                    self.usuario_crud.eliminar(usuario_creado.id_usuario)
                                except Exception:
                                    pass
                                break

                            empleado_datos = EmpleadoCreate(
                                primer_nombre=primer_nombre,
                                segundo_nombre=segundo_nombre,
                                primer_apellido=primer_apellido,
                                segundo_apellido=segundo_apellido,
                                fecha_nacimiento=fecha_nacimiento,
                                telefono=telefono,
                                correo=correo,
                                direccion=direccion,
                                tipo_empleado=tipo_empleado,
                                salario=salario,
                                fecha_ingreso=fecha_ingreso,
                            )

                            empleado = self.empleado_crud.crear(
                                db=self.db,
                                datos_entrada=empleado_datos,
                                usuario_id=usuario_creado.id_usuario,
                                id_sede=sede_sel.id_sede,
                                tipo_documento_id=tipo_doc_sel.id_tipo_documento,
                                documento=documento,
                                creado_por=self.usuario_actual.id_usuario,
                            )
                            if not empleado:
                                print("\nError al crear el empleado. Se revertirá el usuario creado.")
                                # Limpiar usuario si no se creó empleado
                                try:
                                    self.usuario_crud.eliminar(usuario_creado.id_usuario)
                                except Exception:
                                    pass
                                continue

                            print("\n¡Empleado creado exitosamente!")
                            print(f"ID Empleado: {empleado.id_empleado}")

                            otro = (
                                input("\n¿Desea crear otro empleado? (s/n): ")
                                .strip()
                                .lower()
                            )
                            if otro != "s":
                                break
                            else:
                                continue

                        except Exception as e:
                            self.db.rollback()
                            print(f"\nError al crear empleado: {str(e)}")
                            # Intentar limpiar usuario creado si el empleado falló
                            try:
                                if "usuario_creado" in locals() and usuario_creado:
                                    self.usuario_crud.eliminar(usuario_creado.id_usuario)
                            except Exception:
                                pass
                            break

                    except Exception as e:
                        print(f"\nError en el proceso de creación: {str(e)}")
                        break

            elif opcion == 2:
                while True:
                    print("\n--- Listar Empleados ---")
                    print("1. Listar todos los empleados")
                    print("2. Buscar por cargo")
                    print("0. Volver al menú anterior")

                    opcion_listado = int(input("\nSeleccione una opción: ").strip())

                    if opcion_listado == 0:
                        break

                    if opcion_listado == 1:
                        empleados = self.empleado_crud.obtener_activos(
                            self.db, saltar=0, limite=100
                        )
                        self.mostrar_lista_empleados(empleados)

                    elif opcion_listado == 2:
                        cargo_buscar = input("\nIngrese el cargo a buscar: ").strip().lower()
                        empleados = self.empleado_crud.obtener_por_cargo(
                            self.db, cargo_buscar, saltar=0, limite=100
                        )
                        self.mostrar_lista_empleados(
                            empleados,
                            (f" con el cargo: {cargo_buscar}" if cargo_buscar else ""),
                        )
                    else:
                        print("Opción no válida. Intente de nuevo.")
                        continue

                    continuar = (
                        input("\n¿Desea realizar otra búsqueda? (s/n): ")
                        .strip()
                        .lower()
                    )
                    if continuar != "s":
                        break

            elif opcion == 3:
                while True:
                    print("\n--- Editar Empleado ---")
                    empleado_id = input(
                        "Ingrese el ID del empleado a editar (0 para cancelar): "
                    ).strip()

                    if empleado_id == "0":
                        break

                    if not empleado_id:
                        print("Error: Debe ingresar un ID válido.")
                        continue

                    empleado = self.empleado_crud.obtener_por_id(self.db, empleado_id)
                    if not empleado:
                        print("Error: No se encontró un empleado con ese ID.")
                        continue

                    usuario = self.usuario_crud.obtener_por_id(empleado.usuario)
                    if not usuario:
                        print("Error: No se encontró el usuario asociado al empleado.")
                        continue

                    print("\nInformación actual del empleado:")
                    print(
                        f"1. Nombres: {empleado.primer_nombre} {empleado.segundo_nombre or ''}"
                    )
                    print(
                        f"2. Apellidos: {empleado.primer_apellido} {empleado.segundo_apellido or ''}"
                    )
                    print(f"3. Documento: {empleado.documento}")
                    print(f"4. Teléfono: {empleado.telefono}")
                    print(f"5. Correo: {empleado.correo}")
                    print(f"6. Cargo: {empleado.tipo_empleado}")
                    print(f"7. Nombre de usuario: {usuario.nombre_usuario}")

                    print(
                        "\nIngrese los números de los campos que desea modificar (ej: 1,3,5) o 0 para cancelar:"
                    )
                    campos = input("> ").strip().split(",")

                    if "0" in campos:
                        print("Operación cancelada.")
                        break

                    datos_empleado = {}
                    datos_usuario = {}

                    try:
                        if "1" in campos:
                            primer_nombre = input("Nuevo primer nombre: ").strip()
                            segundo_nombre = input(
                                "Nuevo segundo nombre (opcional, presione Enter para omitir): "
                            ).strip()
                            if primer_nombre:
                                datos_empleado["primer_nombre"] = primer_nombre
                                datos_empleado["segundo_nombre"] = (
                                    segundo_nombre if segundo_nombre else None
                                )

                        if "2" in campos:
                            primer_apellido = input("Nuevo primer apellido: ").strip()
                            segundo_apellido = input(
                                "Nuevo segundo apellido (opcional, presione Enter para omitir): "
                            ).strip()
                            if primer_apellido:
                                datos_empleado["primer_apellido"] = primer_apellido
                                datos_empleado["segundo_apellido"] = (
                                    segundo_apellido if segundo_apellido else None
                                )

                        if "3" in campos:
                            print("No se puede modificar el número de documento.")

                        if "4" in campos:
                            telefono = input("Nuevo teléfono: ").strip()
                            if telefono:
                                datos_empleado["telefono"] = telefono

                        if "5" in campos:
                            correo = input("Nuevo correo electrónico: ").strip()
                            if correo:
                                datos_empleado["correo"] = correo

                        if "6" in campos:
                            print("Cargos disponibles:")
                            for i, cargo in enumerate(
                                self.empleado_crud.cargos_permitidos, 1
                            ):
                                print(f"{i}. {cargo}")
                            try:
                                opcion = int(
                                    input("Seleccione el número del cargo: ").strip()
                                )
                                if (
                                    1
                                    <= opcion
                                    <= len(self.empleado_crud.cargos_permitidos)
                                ):
                                    datos_empleado["tipo_empleado"] = (
                                        self.empleado_crud.cargos_permitidos[opcion - 1]
                                    )

                                    if (
                                        datos_empleado["tipo_empleado"]
                                        == "administrador"
                                    ):
                                        datos_usuario["rol"] = (
                                            self.obtener_id_rol_por_nombre("admin")
                                        )
                                    else:
                                        datos_usuario["rol"] = (
                                            self.obtener_id_rol_por_nombre("empleado")
                                        )
                                else:
                                    print(
                                        "Opción no válida. No se actualizará el cargo."
                                    )
                            except (ValueError, IndexError):
                                print("Opción no válida. No se actualizará el cargo.")

                        if "7" in campos:
                            nombre_usuario = input("Nuevo nombre de usuario: ").strip()
                            if nombre_usuario:
                                datos_usuario["nombre_usuario"] = nombre_usuario

                        if datos_empleado or datos_usuario:

                            if datos_empleado:
                                empleado_actualizado = self.empleado_crud.actualizar(
                                    db=self.db,
                                    objeto_db=empleado,
                                    datos_entrada=datos_empleado,
                                    actualizado_por=self.usuario_actual.id_usuario,
                                )
                                if not empleado_actualizado:
                                    print(
                                        "\nError al actualizar los datos del empleado."
                                    )
                                    continue

                            if datos_usuario:
                                usuario_actualizado = self.usuario_crud.actualizar(
                                    db_obj=usuario,
                                    datos_actualizacion=datos_usuario,
                                    actualizado_por=self.usuario_actual.id_usuario,
                                )
                                if not usuario_actualizado:
                                    print("\nError al actualizar los datos de usuario.")
                                    continue

                            print("\n¡Datos actualizados exitosamente!")
                        else:
                            print("\nNo se realizaron cambios.")

                    except Exception as e:
                        print(f"\nError al procesar la actualización: {str(e)}")

                    continuar = (
                        input("\n¿Desea editar otro empleado? (s/n): ").strip().lower()
                    )
                    if continuar != "s":
                        break

            elif opcion == 4:
                while True:
                    print("\n--- Eliminar Empleado ---")
                    empleado_id = input(
                        "Ingrese el ID del empleado a eliminar (0 para cancelar): "
                    ).strip()

                    if empleado_id == "0":
                        break

                    if not empleado_id:
                        print("Error: Debe ingresar un ID válido.")
                        continue

                    empleado = self.empleado_crud.obtener_por_id(self.db, empleado_id)
                    if not empleado:
                        print("Error: No se encontró un empleado con ese ID.")
                        continue

                    print("\nInformación del empleado a eliminar:")
                    print(f"ID: {empleado.id_empleado}")
                    print(
                        f"Nombre: {empleado.primer_nombre} {empleado.segundo_nombre or ''} {empleado.primer_apellido} {empleado.segundo_apellido or ''}"
                    )
                    print(f"Documento: {empleado.documento}")
                    print(f"Cargo: {empleado.tipo_empleado}")

                    confirmacion = (
                        input(
                            "\n¿Está seguro que desea eliminar este empleado? (s/n): "
                        )
                        .strip()
                        .lower()
                    )
                    if confirmacion == "s":
                        try:
                            if self.empleado_crud.eliminar(empleado_id):
                                print("\n¡Empleado eliminado exitosamente!")
                            else:
                                print("\nError: No se pudo eliminar el empleado.")
                        except Exception as e:
                            print(f"\nError al intentar eliminar el empleado: {str(e)}")

                    continuar = (
                        input("\n¿Desea eliminar otro empleado? (s/n): ")
                        .strip()
                        .lower()
                    )
                    if continuar != "s":
                        break

    def _validar_entrada(
        self,
        mensaje,
        tipo="texto",
        requerido=True,
        min_length=1,
        max_length=100,
        opciones=None,
    ):
        """Valida la entrada del usuario según el tipo especificado."""
        while True:
            valor = input(mensaje).strip()

            # Validar campo requerido
            if requerido and not valor:
                print(f"¡Este campo es requerido!")
                continue

            # Si no es requerido y está vacío, devolver None
            if not valor and not requerido:
                return None

            # Validar según el tipo
            if tipo == "texto":
                if len(valor) < min_length or len(valor) > max_length:
                    print(
                        f"El texto debe tener entre {min_length} y {max_length} caracteres."
                    )
                    continue
                return valor

            elif tipo == "email":
                if "@" not in valor or "." not in valor.split("@")[-1]:
                    print("Por favor ingrese un correo electrónico válido.")
                    continue
                if len(valor) > 100:  # Longitud máxima para correos
                    print("El correo no puede tener más de 100 caracteres.")
                    continue
                return valor

            elif tipo == "telefono":
                # Validar que solo contenga números, espacios, guiones y paréntesis
                if not re.match(r"^[0-9\s\-\(\)]+$", valor):
                    print(
                        "El teléfono solo puede contener números, espacios, guiones y paréntesis."
                    )
                    continue
                # Eliminar caracteres no numéricos para verificar la longitud
                numeros = re.sub(r"[^0-9]", "", valor)
                if len(numeros) < 7 or len(numeros) > 15:
                    print("El teléfono debe tener entre 7 y 15 dígitos.")
                    continue
                return valor

            elif tipo == "fecha":
                try:
                    fecha = datetime.strptime(valor, "%Y-%m-%d").date()
                    return fecha
                except ValueError:
                    print("Formato de fecha inválido. Use YYYY-MM-DD")
                    continue

            elif tipo == "numero":
                try:
                    numero = float(valor)
                    if numero < 0:
                        print("El número no puede ser negativo.")
                        continue
                    return numero
                except ValueError:
                    print("Por favor ingrese un número válido.")
                    continue

            elif tipo == "opcion":
                if valor not in opciones:
                    print(
                        f"Opción inválida. Las opciones válidas son: {', '.join(opciones)}"
                    )
                    continue
                return valor

    def mostrar_lista_empleados(self, empleados, texto_sufijo: str = ""):
        """Muestra la lista de empleados. Acepta lista o tupla (lista, total)."""
        if isinstance(empleados, tuple):
            lista, total = empleados
        else:
            lista = empleados
            total = len(lista)

        titulo = f"\n--- Empleados{texto_sufijo} ---"
        print(titulo)
        if not lista:
            print("No se encontraron empleados" + (texto_sufijo or ""))
            return

        for e in lista:
            print(
                f"- ID: {getattr(e, 'id_empleado', '')} | "
                f"{e.primer_nombre} {e.segundo_nombre or ''} {e.primer_apellido} {e.segundo_apellido or ''} | "
                f"Doc: {e.documento} | Cargo: {e.tipo_empleado} | Correo: {e.correo} | Tel: {e.telefono}"
            )
        print(f"Total: {total}")
